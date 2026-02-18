from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReservationMessageCreate(BaseModel):
    message: str
    is_internal: bool = False


class SenderMini(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ReservationMessageResponse(BaseModel):
    id: int
    reservation_id: int
    sender_user_id: int
    message: str
    message_type: str | None = None   # <-- prevent crashes if DB doesn't set it
    is_internal: bool
    is_read: bool
    created_at: datetime
    sender: SenderMini | None = None  # <-- comes from joinedload(sender)

    model_config = ConfigDict(from_attributes=True)
