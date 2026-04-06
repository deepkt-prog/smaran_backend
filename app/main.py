from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from .database import engine, Base
from .routers import auth, events, notifications
from .dependencies import get_current_user_optional, get_db
from fastapi import Depends
from sqlalchemy.orm import Session
import os
from .i18n import get_translations_for_lang
# Create tables (Handled manually via setup_db.py now)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smaran")

from fastapi.responses import HTMLResponse, JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return HTMLResponse(
        status_code=500,
        content=f"<h3>Internal Server Error</h3><pre>{traceback.format_exc()}</pre>"
    )
from starlette.middleware.sessions import SessionMiddleware
from .config import SECRET_KEY

# Mount Static
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, https_only=False, same_site="lax")

from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# Templates
templates = Jinja2Templates(directory="app/templates")

import json
from datetime import date, datetime

def custom_tojson(obj):
    def default_serializer(o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        return str(o)
    return json.dumps(obj, default=default_serializer)

templates.env.filters["tojson"] = custom_tojson



# Include Routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(notifications.router)

@app.get("/", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
@app.get("/scheduled-events", response_class=HTMLResponse)
async def read_root(
    request: Request, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    # Determine Language
    # 1. Cookie (priority for guest/override)
    # 2. User Pref (if logged in)
    # 3. Default "en"
    lang_code = request.cookies.get("language")
    if not lang_code and current_user:
        lang_code = current_user.language_preference
    
    if not lang_code:
        lang_code = "en"
    
    t = get_translations_for_lang(lang_code)

    events_list = []
    if current_user:
        # Fetch events and calculate dates manually since we are in a route handler not calling the API endpoint directly
        # TODO: Refactor this into a service function to avoid duplication with events.py
        from .engine.panchang import engine_instance
        from datetime import date
        current_year = date.today().year
        
        db_events = current_user.events
        MAX_YEARS_LOOKAHEAD = 5
        db_events = current_user.events
        for event in db_events:
            calculated_date = None
            
            # Loop next 5 years to find first future occurrence
            for year_offset in range(MAX_YEARS_LOOKAHEAD):
                search_year = current_year + year_offset
                temp_date = engine_instance.find_event_date(
                    year=search_year,
                    masa=event.masa,
                    paksha=event.paksha,
                    tithi=event.tithi,
                    latitude=current_user.latitude,
                    longitude=current_user.longitude,
                    recurrence_type=event.recurrence_type,
                    return_all=False # We only need the first valid one
                )
                
                if temp_date:
                    calculated_date = temp_date
                    break
            
            # Create a dict-like object or modify event object for template
            if calculated_date:
                event.next_date = calculated_date
            events_list.append(event)
        
        # Filter for Upcoming (Next 30 Days)
        upcoming_events = []
        today = date.today()
        from datetime import timedelta
        thirty_days_later = today + timedelta(days=30)
        
        for e in events_list:
            if hasattr(e, 'next_date') and e.next_date:
                # next_date is a date object
                if today <= e.next_date <= thirty_days_later:
                    upcoming_events.append(e)
                    
        # Sort upcoming by date
        upcoming_events.sort(key=lambda x: x.next_date)
        
    return templates.TemplateResponse(request=request, name="index.html", context={
        "request": request, 
        "title": "Smaran", 
        "user": current_user,
        "events": events_list,
        "upcoming_events": upcoming_events if current_user else [],
        "t": t,
        "current_lang": lang_code
    })

@app.get("/calendar", response_class=HTMLResponse)
async def read_calendar(
    request: Request, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    if not current_user:
        # Redirect to login if not logged in
        return RedirectResponse(url="/auth/login", status_code=303)

    events_list = []
    # Copy-paste logic for now (Refactor later)
    from .engine.panchang import engine_instance
    from datetime import date
    current_year = date.today().year
    
    db_events = current_user.events
    # User Events
    # Calendar View: Fetch all occurrences for this year (and maybe next year to be safe for Jan/Feb overlap?)
    # For now, just Current Year + Next Year (2 years)
    years_to_show = [current_year, current_year + 1] 

    for y in years_to_show:
        # Bulk Fetch (Optimized)
        panchang_map = engine_instance.get_yearly_panchang(y, current_user.latitude, current_user.longitude)
        
        # User Events
        for event in db_events:
            for (m, p, t), dates in panchang_map.items():
                is_match = False
                
                if event.recurrence_type == "yearly":
                    if m == event.masa and p == event.paksha and t == event.tithi:
                        is_match = True
                elif event.recurrence_type == "monthly":
                    if p == event.paksha and t == event.tithi:
                        is_match = True
                elif event.recurrence_type == "paksha":
                    if t == event.tithi:
                        is_match = True
                
                if is_match:
                    for d in dates:
                        events_list.append({
                            "id": event.id,
                            "name": event.name,
                            "next_date": d,
                            "description": event.description,
                            "masa": event.masa,
                            "paksha": event.paksha,
                            "tithi": event.tithi,
                            "recurrence_type": event.recurrence_type,
                            "is_system": False
                        })

        # System Festivals (Always Yearly)
        from .engine.festivals import SYSTEM_FESTIVALS
        for fest in SYSTEM_FESTIVALS:
            key = (fest["masa"], fest["paksha"], fest["tithi"])
            dates = panchang_map.get(key, [])
            for d in dates:
                 events_list.append({
                    "id": fest.get("id"), # System festivals might not have IDs, handle gracefully in template
                    "name": f"🎉 {fest['name']}",
                    "next_date": d,
                    "description": "System Festival",
                    "masa": fest["masa"],
                    "paksha": fest["paksha"],
                    "tithi": fest["tithi"],
                    "recurrence_type": "yearly",
                    "is_system": True
                })
    
    # Determine Language (Duplicated logic, should refactor)
    lang_code = request.cookies.get("language")
    if not lang_code and current_user:
        lang_code = current_user.language_preference
    if not lang_code:
        lang_code = "en"
    t = get_translations_for_lang(lang_code)

    return templates.TemplateResponse(request=request, name="calendar.html", context={
        "request": request, 
        "user": current_user,
        "events": events_list,
        "t": t,
        "current_lang": lang_code
    })

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/init-db")
def init_db():
    try:
        from .database import engine, Base
        import app.models # make sure models are loaded
        Base.metadata.create_all(bind=engine)
        return {"status": "success", "message": "Database tables created successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
