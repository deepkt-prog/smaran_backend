from app.database import SessionLocal
from app.models import User, Event, Notification
import app.models
from app.engine.panchang import engine_instance
from app.services.notifications import notification_service
from datetime import date, timedelta
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_daily_reminders():
    """
    1. Iterate through all users.
    2. For each user, check their events.
    3. Calculate the Gregorian date for each event for the current year.
    4. If the calculated date matches TODAY (or tomorrow for advance reminder), send notification.
    """
    db = SessionLocal()
    today = date.today()
    current_year = today.year
    
    # Check for reminders happening X days in advance? Let's say 1 day advance is good.
    # target_date = today + timedelta(days=1) 
    # For simulation purposes, let's just check for "today" or force a match if we want to test logic.
    # Actually, for the user to "test it themselves", we might need to pretend an event is today.
    # Let's implement robust logic: Check if an event falls on `target_date`.
    
    target_check_date = today # Check for events happening TODAY
    
    logger.info(f"Processing reminders for target date: {target_check_date}")

    try:
        users = db.query(User).all()
        for user in users:
            logger.info(f"Checking events for user: {user.email}")
            for event in user.events:
                # Calculate date for this event in current year
                try:
                    event_date = engine_instance.find_event_date(
                        year=current_year,
                        masa=event.masa,
                        paksha=event.paksha,
                        tithi=event.tithi,
                        latitude=user.latitude,
                        longitude=user.longitude
                    )
                    
                    if event_date:
                        days_diff = (event_date - today).days
                        
                        # Logic: Notify if event is today (0) or tomorrow (1)
                        if days_diff == 0:
                            subject = f"Smaran Reminder: {event.name} is TODAY"
                            body = f"Namaste {user.email},\n\nThis is a reminder that '{event.name}' is falling on today, {event_date}.\n\n- Team Smaran"
                            notification_service.send_email(user.email, subject, body)
                            
                            # Create In-App Notification
                            new_notif = app.models.Notification(
                                user_id=user.id,
                                message=f"Reminder: {event.name} is today!",
                                type="reminder"
                            )
                            db.add(new_notif)
                            db.commit()

                            if user.whatsapp_opt_in:
                                notification_service.send_whatsapp(user.mobile_number, body)
                                
                        elif days_diff == 1:
                            subject = f"Smaran Reminder: {event.name} is TOMORROW"
                            body = f"Namaste {user.email},\n\nThis is a reminder that '{event.name}' is falling on tomorrow, {event_date}.\n\n- Team Smaran"
                            notification_service.send_email(user.email, subject, body)
                            
                            # Create In-App Notification
                            new_notif = app.models.Notification(
                                user_id=user.id,
                                message=f"Reminder: {event.name} is tomorrow!",
                                type="reminder"
                            )
                            db.add(new_notif)
                            db.commit()

                except Exception as e:
                    logger.error(f"Error calculating date for event {event.name}: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    process_daily_reminders()
