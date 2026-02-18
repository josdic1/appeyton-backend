# app/schemas/dining_room.py
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict

class DiningRoomCreate(BaseModel):
    name: str
    legal_capacity: int = 100
    is_active: bool = True
    display_order: int = 0
    meta: dict[str, Any] | None = None

class DiningRoomUpdate(BaseModel):
    name: str | None = None
    legal_capacity: int | None = None
    is_active: bool | None = None
    display_order: int | None = None
    meta: dict[str, Any] | None = None

class DiningRoomResponse(BaseModel):
    id: int
    name: str
    legal_capacity: int
    setup_capacity: int = 0  
    is_active: bool
    display_order: int
    meta: dict[str, Any] | None = None
    created_by_user_id: int | None = None
    updated_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime

    # Use ONLY model_config for Pydantic V2
    model_config = ConfigDict(from_attributes=True)