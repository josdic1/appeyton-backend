# app/schemas/notification.py
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, computed_field

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    notification_type: str
    channel: str
    priority: str
    subject: Optional[str] = None
    message: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    status: str
    created_at: datetime
    read_at: Optional[datetime] = None
    
    @computed_field
    @property
    def is_read(self) -> bool:
        """Dynamically determine read status based on timestamp"""
        return self.read_at is not None

    model_config = ConfigDict(from_attributes=True)