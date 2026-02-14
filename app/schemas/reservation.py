# app/schemas/reservation.py
from __future__ import annotations
from datetime import datetime, date as date_type, time as time_type
from typing import Any

from pydantic import BaseModel, ConfigDict


class ReservationCreate(BaseModel):
    dining_room_id: int
    table_id: int
    date: date_type
    meal_type: str
    start_time: time_type
    end_time: time_type
    notes: str | None = None
    meta: dict[str, Any] | None = None


class ReservationUpdate(BaseModel):
    dining_room_id: int | None = None
    table_id: int | None = None
    date: date_type | None = None
    meal_type: str | None = None
    start_time: time_type | None = None
    end_time: time_type | None = None
    status: str | None = None
    notes: str | None = None
    meta: dict[str, Any] | None = None


class ReservationResponse(BaseModel):
    id: int
    user_id: int
    dining_room_id: int
    table_id: int
    date: date_type
    meal_type: str
    start_time: time_type
    end_time: time_type
    status: str
    party_size: int  # Computed from attendees
    notes: str | None
    meta: dict[str, Any] | None
    created_by_user_id: int | None
    cancelled_by_user_id: int | None
    confirmed_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)