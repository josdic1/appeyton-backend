# app/schemas/table_entity.py
from __future__ import annotations
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class TableEntityCreate(BaseModel):
    dining_room_id: int
    table_number: int
    seat_count: int
    position_x: int | None = None
    position_y: int | None = None
    meta: dict[str, Any] | None = None


class TableEntityUpdate(BaseModel):
    table_number: int | None = None
    seat_count: int | None = None
    position_x: int | None = None
    position_y: int | None = None
    meta: dict[str, Any] | None = None


class TableEntityResponse(BaseModel):
    id: int
    dining_room_id: int
    table_number: int
    seat_count: int
    position_x: int | None
    position_y: int | None
    meta: dict[str, Any] | None
    
    # Audit fields - ADDED
    created_by_user_id: int | None
    updated_by_user_id: int | None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)