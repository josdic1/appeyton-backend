# app/schemas/reservation.py
from __future__ import annotations
from datetime import datetime, date, time
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.reservation_attendee import ReservationAttendeeResponse
from app.schemas.table_entity import TableEntityResponse
from app.schemas.reservation_message import ReservationMessageResponse

class ReservationBase(BaseModel):
    date: date
    meal_type: str
    start_time: time
    end_time: time
    dining_room_id: int
    table_id: int
    notes: Optional[str] = None

class ReservationCreate(ReservationBase):
    attendees: List[ReservationAttendeeResponse]

class ReservationUpdate(BaseModel):
    dining_room_id: Optional[int] = None
    table_id: Optional[int] = None
    status: Optional[int] = None # Or str depending on status type
    notes: Optional[str] = None

class ReservationResponse(ReservationBase):
    id: int
    user_id: int
    status: str
    fired_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # ── NESTED DATA (Matches selectinload) ──
    table: Optional[TableEntityResponse] = None
    attendees: List[ReservationAttendeeResponse] = []
    messages: List[ReservationMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)