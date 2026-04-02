from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from typing import Optional
from sqlalchemy.orm import Session
from .. import schemas, models, database
from ..engine.panchang import engine_instance
from datetime import date
from ..dependencies import get_current_user, get_db

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/calculate-date", response_model=date)
def calculate_tithi_date(request: schemas.TithiRequest):
    """
    Calculate Gregorian date for a given Tithi.
    """
    found_dates = engine_instance.find_event_date(
        year=request.year,
        masa=request.masa,
        paksha=request.paksha,
        tithi=request.tithi,
        latitude=request.latitude,
        longitude=request.longitude,
        recurrence_type="yearly",
        return_all=True
    )
    
    if found_dates:
        # Return the first one, usually there's only one per year for yearly event
        # If there are two (rare, adhika/kshaya), return the first one
        return found_dates[0]
    
    raise HTTPException(status_code=404, detail="Could not find date for this Tithi in the given year")

@router.post("/reverse-calc", response_model=schemas.ReverseCalcResponse)
def reverse_calculate_panchang(request: schemas.ReverseCalcRequest):
    """
    Calculate Tithi/Masa/Paksha from a Gregorian Date.
    """
    print(f"DEBUG: Received Reverse Calc Request: date={request.date}, lat={request.latitude}, lon={request.longitude}")
    try:
        result = engine_instance.get_panchang_from_date(
            date_obj=request.date,
            latitude=request.latitude,
            longitude=request.longitude
        )
        print(f"DEBUG: Calculation Result: {result}")
        
        if not result:
            print("DEBUG: Result was None/Empty")
            raise HTTPException(status_code=500, detail="Could not calculate Panchang")
            
        return result
    except Exception as e:
        print(f"DEBUG: Exception in reverse_calc: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[schemas.EventDisplay])
def list_events(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    events = current_user.events
    display_events = []
    current_year = date.today().year
    
    for event in events:
        # Calculate for current year
        calculated_date = engine_instance.find_event_date(
            year=current_year,
            masa=event.masa,
            paksha=event.paksha,
            tithi=event.tithi,
            latitude=current_user.latitude,
            longitude=current_user.longitude
        )
        
        # If date has passed for this year, maybe calculate for next year? 
        # For MVP, just show this year's date even if passed, or None if calculation fails
        
        event_dict = schemas.Event.from_orm(event).dict()
        event_display = schemas.EventDisplay(**event_dict, next_date=calculated_date)
        display_events.append(event_display)
        
    return display_events

@router.post("/")
def create_event(
    name: str = Form(...),
    masa: Optional[str] = Form(None),
    paksha: Optional[str] = Form(None),
    tithi: int = Form(...),
    recurrence_type: str = Form("yearly"),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    print(f"DEBUG: create_event called. Name={name}, Tithi={tithi}, Recurrence={recurrence_type}")
    # Validation logic here if needed (e.g. if yearly, masa is required)
    
    new_event = models.Event(
        user_id=current_user.id,
        name=name,
        masa=masa,
        paksha=paksha,
        tithi=tithi,
        recurrence_type=recurrence_type,
        description=description
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return RedirectResponse(url="/", status_code=303)

@router.put("/{event_id}", response_model=schemas.Event)
def update_event(
    event_id: int,
    event_update: schemas.EventUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.user_id == current_user.id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    for key, value in event_update.dict(exclude_unset=True).items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event

    db.delete(db_event)
    db.commit()
    return {"detail": "Event deleted successfully"}

# FAMILY & MEMORY ENDPOINTS

@router.get("/family", response_model=list[schemas.EventDisplay])
def list_family_events(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Fetch events from other family members.
    """
    if not current_user.family_id:
        return []
        
    # Get other family members
    family_members = db.query(models.User).filter(
        models.User.family_id == current_user.family_id,
        models.User.id != current_user.id
    ).all()
    
    member_ids = [u.id for u in family_members]
    if not member_ids:
        return []
        
    family_events = db.query(models.Event).filter(models.Event.user_id.in_(member_ids)).all()
    
    display_events = []
    current_year = date.today().year
    
    for event in family_events:
        calculated_date = engine_instance.find_event_date(
            year=current_year,
            masa=event.masa,
            paksha=event.paksha,
            tithi=event.tithi,
            latitude=current_user.latitude, 
            longitude=current_user.longitude
        )
        
        event_dict = schemas.Event.from_orm(event).dict()
        # Add Owner Name to description or separate field?
        # Schema might need update to include owner_name. For now append to description or handle in frontend.
        # Let's trust the schema can handle extra fields if we pass them, or just rely on IDs.
        # Actually simplest is to just return raw event for now.
        
        event_display = schemas.EventDisplay(**event_dict, next_date=calculated_date)
        display_events.append(event_display)
        
    return display_events

from fastapi import UploadFile, File
import shutil
import os

@router.post("/{event_id}/memory")
async def upload_memory(
    event_id: int,
    file: UploadFile = File(...),
    caption: str = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify access (Owner or Family Member)
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
        
    # Check permission: Owner OR same Family
    is_owner = event.user_id == current_user.id
    is_family = False
    if current_user.family_id:
        owner = db.query(models.User).filter(models.User.id == event.user_id).first()
        if owner and owner.family_id == current_user.family_id:
            is_family = True
            
    if not (is_owner or is_family):
        raise HTTPException(403, "Not authorized to add memories to this event")

    # Save File
    upload_dir = "app/static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_ext = os.path.splitext(file.filename)[1]
    import uuid
    safe_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    relative_path = f"/static/uploads/{safe_filename}"
    
    new_memory = models.EventMemory(
        event_id=event_id,
        media_type="image", # Assume image for MVP
        media_url=relative_path,
        caption=caption
    )
    db.add(new_memory)
    db.commit()
    
    return RedirectResponse(url="/", status_code=303)

@router.get("/{event_id}/memories")
def get_memories(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.EventMemory).filter(models.EventMemory.event_id == event_id).all()
