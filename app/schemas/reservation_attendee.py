# app/schemas/reservation_attendee.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, List, Dict

from pydantic import BaseModel, ConfigDict, model_validator, Field


class ReservationAttendeeCreate(BaseModel):
    """
    Used for both initial POST and the Sync PATCH.
    Optional ID allows upserting instead of duplicating.
    """
    id: Optional[int] = None
    reservation_id: Optional[int] = None

    member_id: Optional[int] = None
    seat_id: Optional[int] = None

    # Optional because member-attendees can be created with member_id only
    name: Optional[str] = Field(None, max_length=120)

    # Optional because backend should normalize this ("member" vs "guest")
    attendee_type: Optional[str] = Field(None, max_length=20)

    dietary_restrictions: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def validate_member_or_guest(self) -> "ReservationAttendeeCreate":
        # Member attendee: allow missing name/type (backend will fill)
        if self.member_id is not None:
            if self.name is not None and len(self.name.strip()) == 0:
                self.name = None
            return self

        # Guest attendee: require a non-empty name
        if self.name is None or len(self.name.strip()) == 0:
            raise ValueError("Guest attendee requires a non-empty name")

        self.name = self.name.strip()
        return self


class ReservationAttendeeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    seat_id: Optional[int] = None
    attendee_type: Optional[str] = Field(None, max_length=20)
    dietary_restrictions: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


class ReservationAttendeeResponse(BaseModel):
    id: int
    reservation_id: int
    member_id: Optional[int] = None
    seat_id: Optional[int] = None
    name: str
    attendee_type: str
    dietary_restrictions: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None
    created_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReservationAttendeeSyncList(BaseModel):
    """Used for bulk updating the guest list of a reservation"""
    attendees: List[ReservationAttendeeCreate]