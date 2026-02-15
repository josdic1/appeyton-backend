# app/schemas/reservation_attendee.py
from __future__ import annotations
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class ReservationAttendeeCreate(BaseModel):
    reservation_id: int  # ← THIS LINE IS CRITICAL
    member_id: Optional[int] = None
    name: Optional[str] = None
    attendee_type: str
    dietary_restrictions: Optional[dict] = None
    meta: Optional[dict] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v, info):
        # If it's a guest, name is required
        if info.data.get('attendee_type') == 'guest' and not v:
            raise ValueError('Name is required for guests')
        return v


class ReservationAttendeeUpdate(BaseModel):
    name: str | None = None
    attendee_type: str | None = None
    dietary_restrictions: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None


class ReservationAttendeeResponse(BaseModel):
    id: int
    reservation_id: int
    member_id: int | None
    name: str
    attendee_type: str
    dietary_restrictions: dict[str, Any] | None
    meta: dict[str, Any] | None
    created_by_user_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)