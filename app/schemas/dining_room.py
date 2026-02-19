# app/schemas/dining_room.py
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field

class DiningRoomBase(BaseModel):
    """Shared fields for all DiningRoom schemas"""
    name: str = Field(..., min_length=1, max_length=100)
    legal_capacity: int = Field(default=100, ge=1)
    is_active: bool = True
    display_order: int = 0
    meta: Dict[str, Any] | None = None

class DiningRoomCreate(DiningRoomBase):
    """Schema for creating a new dining room"""
    pass

class DiningRoomUpdate(BaseModel):
    """Schema for updating an existing dining room (all fields optional)"""
    name: str | None = Field(None, min_length=1, max_length=100)
    legal_capacity: int | None = Field(None, ge=1)
    is_active: bool | None = None
    display_order: int | None = None
    meta: Dict[str, Any] | None = None

class DiningRoomResponse(DiningRoomBase):
    """Schema for returning dining room data"""
    id: int
    # setup_capacity is the hybrid_property from the SQLAlchemy model
    setup_capacity: int = 0  
    created_by_user_id: int | None = None
    updated_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)