# app/schemas/reservation_attendee.py
from __future__ import annotations
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ReservationAttendeeCreate(BaseModel):
    member_id: int | None = None
    name: str  # ← FIXED: Required (database has NOT NULL)
    attendee_type: str = "guest"
    dietary_restrictions: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None


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
    created_by_user_id: int | None  # ← Added for audit trail
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)