# app/schemas/reservation_attendee.py
from __future__ import annotations
from datetime import datetime
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, ConfigDict, field_validator

class ReservationAttendeeCreate(BaseModel):
    """
    Used for both initial POST and the Sync PATCH.
    The optional ID allows the backend to update existing rows instead of duplicating them.
    """
    id: Optional[int] = None 
    reservation_id: Optional[int] = None
    member_id: Optional[int] = None
    seat_id: Optional[int] = None
    name: str 
    attendee_type: str # 'self', 'spouse', 'child', 'guest'
    dietary_restrictions: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Guest name cannot be empty')
        return v.strip()

class ReservationAttendeeUpdate(BaseModel):
    """Used for individual guest PATCH requests"""
    name: Optional[str] = None
    seat_id: Optional[int] = None
    attendee_type: Optional[str] = None
    dietary_restrictions: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None

class ReservationAttendeeResponse(BaseModel):
    """The shape sent to React for Visit Management and Manifests"""
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
    """Wrapper for the batch reconciliation payload"""
    attendees: List[ReservationAttendeeCreate]