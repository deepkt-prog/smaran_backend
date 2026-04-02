from datetime import date, datetime 
from typing import Optional, List
from pydantic import BaseModel
    
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
