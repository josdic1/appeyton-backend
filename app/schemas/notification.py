# app/schemas/notification.py
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, computed_field, Field

class NotificationCreate(BaseModel):
    """Used by services to queue a new notification"""
    user_id: int
    notification_type: str = Field(..., max_length=50)
    channel: str = Field(..., max_length=20)
    priority: str = "normal"
    subject: Optional[str] = Field(None, max_length=200)
    message: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None

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
    
    # Delivery Status
    status: str
    retry_count: int
    error_message: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    
    @computed_field
    @property
    def is_read(self) -> bool:
        """Dynamically determine read status based on timestamp"""
        return self.read_at is not None

    @computed_field
    @property
    def has_failed(self) -> bool:
        """Easy flag for frontend to highlight errors"""
        return self.status == "failed"

    model_config = ConfigDict(from_attributes=True)