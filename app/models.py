from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    mobile_number = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    timezone = Column(String)
    language_preference = Column(String, default="en")
    
    # Email Verification & Notifications
    is_email_verified = Column(Boolean, default=False)
    email_notifications_enabled = Column(Boolean, default=False)
    otp_code = Column(String, nullable=True)
    otp_created_at = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)

    whatsapp_opt_in = Column(Boolean, default=False)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)

    events = relationship("Event", back_populates="owner")
    notifications = relationship("Notification", back_populates="user")
    family = relationship("Family", back_populates="members")

class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    invite_code = Column(String, unique=True, index=True) # 6-digit code
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    members = relationship("User", back_populates="family")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    masa = Column(String, nullable=True)  # Month name e.g., 'Bhadrapada'
    paksha = Column(String, nullable=True) # 'Shukla' or 'Krishna'
    tithi = Column(Integer) # 1-15
    recurrence_type = Column(String, default="yearly") # 'yearly', 'monthly', 'paksha'
    description = Column(String, nullable=True)
    is_recurring = Column(Boolean, default=True)
    suggested_action = Column(String, nullable=True) # e.g. "Book Brahman", "Vrat Recipes"

    owner = relationship("User", back_populates="events")
    memories = relationship("EventMemory", back_populates="event", cascade="all, delete-orphan")

class EventMemory(Base):
    __tablename__ = "event_memories"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    media_type = Column(String) # 'image', 'audio', 'text'
    media_url = Column(String, nullable=True)
    caption = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    event = relationship("Event", back_populates="memories")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    is_read = Column(Boolean, default=False)
    type = Column(String, default="info") # 'reminder', 'system', 'alert'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")
