# app/schemas/reservation_message.py
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReservationMessageCreate(BaseModel):
    message: str = Field(..., min_length=1)
    is_internal: bool = False
    parent_message_id: int | None = None


class SenderMini(BaseModel):
    """Lean user data for message headers"""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ReservationMessageResponse(BaseModel):
    id: int
    reservation_id: int
    sender_user_id: int
    
    message: str
    message_type: str | None = "text"
    is_internal: bool
    
    # Read Status
    is_read: bool
    read_at: datetime | None = None
    
    # Threading support
    parent_message_id: int | None = None
    
    created_at: datetime
    
    # Populated via joinedload in the service layer
    sender: SenderMini | None = None

    model_config = ConfigDict(from_attributes=True)