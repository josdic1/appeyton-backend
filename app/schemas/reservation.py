# app/schemas/reservation.py
from __future__ import annotations
from datetime import datetime, date, time
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.reservation_attendee import (
    ReservationAttendeeCreate,
    ReservationAttendeeResponse,
)
from app.schemas.table_entity import TableEntityResponse
from app.schemas.reservation_message import ReservationMessageResponse

class ReservationBase(BaseModel):
    # Made these Optional because the frontend sends 'reservation_time' instead
    date: Optional[date] = None
    meal_type: Optional[str] = Field(None, max_length=30)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    
    dining_room_id: int
    # Made Optional so you can book a ROOM without picking a TABLE first
    table_id: Optional[int] = None
    notes: Optional[str] = None

class ReservationCreate(ReservationBase):
    # Added to match your ReservationFormModal.jsx payload
    reservation_time: datetime 
    party_size: int = 1
    
    # Allows adding attendees at the moment of creation
    attendees: List[ReservationAttendeeCreate] = []

class ReservationUpdate(BaseModel):
    date: Optional[date] = None
    meal_type: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    dining_room_id: Optional[int] = None
    table_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class ReservationResponse(ReservationBase):
    id: int
    user_id: int
    status: str
    
    fired_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime

    party_size: int = 0
    
    table: Optional[TableEntityResponse] = None
    attendees: List[ReservationAttendeeResponse] = []
    messages: List[ReservationMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)