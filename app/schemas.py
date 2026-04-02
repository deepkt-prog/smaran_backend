from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

class UserBase(BaseModel):
    email: EmailStr
    mobile_number: str
    latitude: float
    longitude: float
    timezone: str
    language_preference: str = "en"
    whatsapp_opt_in: bool = False

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True
    
    class Config:
        from_attributes = True

class EventBase(BaseModel):
    name: str
    masa: str
    paksha: str
    tithi: int
    is_recurring: bool = True

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    masa: Optional[str] = None
    paksha: Optional[str] = None
    tithi: Optional[int] = None
    is_recurring: Optional[bool] = None

class Event(EventBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class EventDisplay(Event):
    next_date: Optional[date] = None


class TithiRequest(BaseModel):
    year: int
    masa: str
    paksha: str
    tithi: int
    latitude: float
    longitude: float

class ReverseCalcRequest(BaseModel):
    date: date
    latitude: float
    longitude: float

class ReverseCalcResponse(BaseModel):
    masa: str
    paksha: str
    tithi: int


class NotificationBase(BaseModel):
    message: str
    is_read: bool = False
    type: str = "info"

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
