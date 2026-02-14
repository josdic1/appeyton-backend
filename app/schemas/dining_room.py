# app/schemas/dining_room.py
from __future__ import annotations
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class DiningRoomCreate(BaseModel):
    name: str
    capacity: int
    is_active: bool = True
    display_order: int = 0
    meta: dict[str, Any] | None = None


class DiningRoomUpdate(BaseModel):
    name: str | None = None
    capacity: int | None = None
    is_active: bool | None = None
    display_order: int | None = None
    meta: dict[str, Any] | None = None


class DiningRoomResponse(BaseModel):
    id: int
    name: str
    capacity: int
    is_active: bool
    display_order: int
    meta: dict[str, Any] | None
    
    # Audit fields - ADDED
    created_by_user_id: int | None
    updated_by_user_id: int | None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)