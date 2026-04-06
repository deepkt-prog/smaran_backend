from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..dependencies import get_current_user
from passlib.context import CryptContext
from typing import Optional
from authlib.integrations.starlette_client import OAuth
from ..config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth Setup
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html", context={"request": request})

@router.post("/signup")
async def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    mobile_number: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return templates.TemplateResponse(request=request, name="signup.html", context={"request": request, "error": "Email already registered"})
    
    hashed_password = get_password_hash(password)
    new_user = models.User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        mobile_number=mobile_number,
        latitude=latitude,
        longitude=longitude,
        timezone="UTC"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # In a real app, set cookie/session here
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request})

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(request=request, name="login.html", context={"request": request, "error": "Invalid credentials"})
    
    import datetime
    user.last_login = datetime.datetime.utcnow()
    db.commit()

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    # Simple "session" cookie for MVP
    response.set_cookie(key="user_id", value=str(user.id))
    return response

@router.get("/logout")
async def logout_get(request: Request):
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("user_id")
    request.session.clear()
    return response

# @router.post("/request-otp")
# def request_otp(
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     from ..utils.email import generate_otp, send_otp_email
#     
#     otp = generate_otp()
#     if send_otp_email(current_user.email, otp):
#         current_user.otp_code = otp
#         current_user.otp_created_at = datetime.utcnow()
#         db.commit()
#         return {"message": "OTP sent successfully"}
#     else:
#         # If email fails (e.g. no config), maybe return error or mocked success for dev?
#         # For now, return error to prompt user to config
#         raise HTTPException(status_code=500, detail="Failed to send email. Check server logs/configuration.")

# @router.post("/verify-otp")
# def verify_otp(
#     otp: str = Form(...),
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     
#     if not current_user.otp_code or not current_user.otp_created_at:
#          raise HTTPException(status_code=400, detail="No OTP requested")
#          
#     # Check expiry (10 mins)
#     if datetime.utcnow() - current_user.otp_created_at > timedelta(minutes=10):
#          raise HTTPException(status_code=400, detail="OTP expired")
#          
#     if current_user.otp_code == otp:
#         current_user.is_email_verified = True
#         current_user.email_notifications_enabled = True # Auto-enable on verify
#         current_user.otp_code = None # Clear OTP
#         db.commit()
#         return {"message": "Email verified successfully"}
#     else:
#         raise HTTPException(status_code=400, detail="Invalid OTP")

# @router.post("/toggle-email-notifications")
# def toggle_email_notifications(
#     enabled: bool = Form(...),
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(get_current_user)
# ):
#     if not current_user.is_email_verified:
#         raise HTTPException(status_code=400, detail="Email not verified")
#         
#     current_user.email_notifications_enabled = enabled
#     db.commit()
#     return {"status": "updated", "enabled": enabled}

@router.post("/logout")
async def logout_post(request: Request):
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("user_id")
    request.session.clear() # Clear OAuth session data
    return response

@router.post("/set-language")
async def set_language(
    request: Request,
    language: str = Form(...),
    db: Session = Depends(get_db)
):
    valid_langs = ["en", "hi", "mr", "gu"]
    language = language if language in valid_langs else "en"
    
    # Update user preference if logged in
    user_id = request.cookies.get("user_id")
    if user_id:
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if user:
            user.language_preference = language
            db.commit()
            
    # Always set cookie for persistence (even if not logged in or as fallback)
    response = RedirectResponse(url=request.headers.get("referer", "/"), status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="language", value=language)
    return response

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        # This usually happens if user cancels or config is wrong
        return templates.TemplateResponse(request=request, name="login.html", context={"request": request, "error": f"Google Login Failed: {str(e)}"})
        
    user_info = token.get('userinfo')
    if not user_info:
        # Try fetching if not in token
        user_info = await oauth.google.userinfo(token=token)

    email = user_info.get("email")
    name = user_info.get("name")
    
    if not email:
        return templates.TemplateResponse(request=request, name="login.html", context={"request": request, "error": "Could not get email from Google."})

    # Check if user exists
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        # Create new user
        # We need a random password or mark as 'social_login'
        import secrets
        random_password = secrets.token_urlsafe(16)
        hashed_password = get_password_hash(random_password)
        
        # Determine default location/timezone or ask user later
        new_user = models.User(
            email=email,
            full_name=name,
            hashed_password=hashed_password,
            mobile_number="", # Not provided by Google usually
            latitude=19.0760, # Default Mumbai
            longitude=72.8777,
             timezone="UTC",
             is_email_verified=True, # Trusted from Google
        )
        # Handle last_login if column exists (it should now)
        import datetime
        try:
             new_user.last_login = datetime.datetime.utcnow()
        except:
             pass

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user
    else:
        # Update Last Login
        import datetime
        user.last_login = datetime.datetime.utcnow()
        db.commit()
    
    # Login
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="user_id", value=str(user.id))
    return response
# Helper to get current user for templates (duplicated for now to avoid circular imports if dependencies imports this router)
# Actually, better to use dependencies.get_current_user_optional in main.py but we need it here? No, auth router doesn't need it.

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, current_user = Depends(get_current_user)):
    return templates.TemplateResponse(request=request, name="profile.html", context={"request": request, "user": current_user})

@router.post("/profile")
async def update_profile(
    request: Request,
    action: str = Form(...),
    full_name: Optional[str] = Form(None),
    mobile_number: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        if action == "update_profile":
            user_in_db = db.merge(current_user)
            user_in_db.full_name = full_name
            user_in_db.mobile_number = mobile_number
            db.add(user_in_db)
            db.commit()
            db.refresh(user_in_db)
            return templates.TemplateResponse(request=request, name="profile.html", context={
                "request": request, 
                "user": user_in_db, 
                "message": "Profile updated successfully!"
            })
            
        elif action == "update_password":
            if not password or len(password) < 6:
                return templates.TemplateResponse(request=request, name="profile.html", context={
                    "request": request, 
                    "user": current_user, 
                    "error": "Password must be at least 6 characters."
                })
            
            user_in_db = db.merge(current_user)
            user_in_db.hashed_password = get_password_hash(password)
            db.add(user_in_db)
            db.commit()
            return templates.TemplateResponse(request=request, name="profile.html", context={
                "request": request, 
                "user": user_in_db, 
                "message": "Password changed successfully!"
            })
            
    except Exception as e:
        return templates.TemplateResponse(request=request, name="profile.html", context={
            "request": request, 
            "user": current_user, 
            "error": f"An error occurred: {str(e)}"
        })
    
    
    return RedirectResponse(url="/auth/profile", status_code=status.HTTP_303_SEE_OTHER)

# FAMILY MODULE ROUTES

@router.post("/family/create")
async def create_family(
    request: Request,
    family_name: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    import secrets
    import string
    
    if current_user.family_id:
        return templates.TemplateResponse(request=request, name="profile.html", context={
            "request": request, 
            "user": current_user, 
            "error": "You are already in a family. Leave it first to create a new one."
        })

    # Generate Invite Code
    chars = string.ascii_uppercase + string.digits
    invite_code = ''.join(secrets.choice(chars) for _ in range(6))
    
    # Ensure unique code (simple check for MVP)
    while db.query(models.Family).filter(models.Family.invite_code == invite_code).first():
        invite_code = ''.join(secrets.choice(chars) for _ in range(6))

    new_family = models.Family(name=family_name, invite_code=invite_code)
    db.add(new_family)
    db.commit()
    db.refresh(new_family)
    
    # Add user to family
    user_in_db = db.merge(current_user)
    user_in_db.family_id = new_family.id
    db.commit()
    
    return templates.TemplateResponse(request=request, name="profile.html", context={
        "request": request, 
        "user": user_in_db, 
        "message": f"Family '{family_name}' created! Invite Code: {invite_code}"
    })

@router.post("/family/join")
async def join_family(
    request: Request,
    invite_code: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.family_id:
        return templates.TemplateResponse(request=request, name="profile.html", context={
            "request": request, 
            "user": current_user, 
            "error": "You are already in a family."
        })

    family = db.query(models.Family).filter(models.Family.invite_code == invite_code.upper()).first()
    
    if not family:
        return templates.TemplateResponse(request=request, name="profile.html", context={
            "request": request, 
            "user": current_user, 
            "error": "Invalid Invite Code."
        })
        
    user_in_db = db.merge(current_user)
    user_in_db.family_id = family.id
    db.commit()
    
    return templates.TemplateResponse(request=request, name="profile.html", context={
        "request": request, 
        "user": user_in_db, 
        "message": f"Joined '{family.name}' successfully!"
    })

@router.post("/family/leave")
async def leave_family(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not current_user.family_id:
        return RedirectResponse(url="/auth/profile", status_code=303)
        
    user_in_db = db.merge(current_user)
    user_in_db.family_id = None
    db.commit()
    
    return RedirectResponse(url="/auth/profile", status_code=303)
