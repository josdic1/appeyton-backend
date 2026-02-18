# app/schemas/reservation_message.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ReservationMessageCreate(BaseModel):
    message: str
    is_internal: bool = False  # Staff can make internal notes

class ReservationMessageResponse(BaseModel):
    id: int
    reservation_id: int
    sender_user_id: int
    sender_name: str  # We will inject this manually or via relation
    message: str
    message_type: str
    is_internal: bool
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)