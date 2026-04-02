from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)

@router.get("/", response_model=List[schemas.Notification])
def read_notifications(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Lazy Generation: Check/Create notifications for today/tomorrow
    check_for_upcoming_events(db, current_user)

    notifications = db.query(models.Notification)\
        .filter(models.Notification.user_id == current_user.id)\
        .order_by(models.Notification.created_at.desc())\
        .offset(skip).limit(limit).all()
    return notifications

from ..engine.panchang import engine_instance
from datetime import date, timedelta

def check_for_upcoming_events(db: Session, user: models.User):
    # This logic aims to ensure a notification exists if an event is today or tomorrow
    # It avoids duplicates by checking if a notification with specific content already exists for today
    
    events = user.events
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # We only care about Today and Tomorrow for alerts
    target_dates = [today, tomorrow]
    
    for event in events:
        # 1. Calc Next Date
        # We need to see if the event falls on today or tomorrow.
        # find_event_date returns the date in the Requested Year.
        # We should check for current year.
        
        # Optimization: We can reuse the same find_event_date logic from main.py
        # But for simplicity here, let's just ask the engine.
        
        next_date = engine_instance.find_event_date(
            year=today.year,
            masa=event.masa,
            paksha=event.paksha,
            tithi=event.tithi,
            latitude=user.latitude,
            longitude=user.longitude
        )
        
        if not next_date: continue
        
        is_today = next_date == today
        is_tomorrow = next_date == tomorrow
        
        if is_today or is_tomorrow:
            # Prepare Message
            msg = ""
            if is_today:
                msg = f"Today is {event.name}!"
            else:
                msg = f"Tomorrow is {event.name}."
            
            # Check if this notification already exists for this user (fuzzy check on message content to avoid spam)
            # A better way would be a unique constraint or deduplication key, but for now:
            # Check if we created this notification TODAY.
            
            # Find notifications created today with similar message
            start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            exists = db.query(models.Notification).filter(
                models.Notification.user_id == user.id,
                models.Notification.created_at >= start_of_day,
                models.Notification.message == msg
            ).first()
            
            if not exists:
                new_n = models.Notification(
                    user_id=user.id,
                    message=msg,
                    type="event_reminder"
                )
                db.add(new_n)
                db.commit()

from datetime import datetime

@router.post("/{notification_id}/read", response_model=schemas.Notification)
def mark_notification_read(
    notification_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    notification = db.query(models.Notification)\
        .filter(models.Notification.id == notification_id, models.Notification.user_id == current_user.id)\
        .first()
        
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification

@router.post("/test", response_model=schemas.Notification)
def create_test_notification(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Create a dummy notification for testing
    new_notif = models.Notification(
        user_id=current_user.id,
        message="This is a test notification from Smaran!",
        type="system"
    )
    db.add(new_notif)
    db.commit()
    db.refresh(new_notif)
    return new_notif
