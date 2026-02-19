# app/schemas/table_entity.py
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field


class TableEntityBase(BaseModel):
    """Base fields for table entities"""
    table_number: int = Field(..., ge=1)
    seat_count: int = Field(..., ge=1)
    position_x: int | None = None
    position_y: int | None = None
    meta: Dict[str, Any] | None = None


class TableEntityCreate(TableEntityBase):
    """Required fields for creating a table"""
    dining_room_id: int


class TableEntityUpdate(BaseModel):
    """Optional fields for updating a table"""
    table_number: int | None = Field(None, ge=1)
    seat_count: int | None = Field(None, ge=1)
    position_x: int | None = None
    position_y: int | None = None
    dining_room_id: int | None = None
    meta: Dict[str, Any] | None = None


class TableEntityResponse(TableEntityBase):
    """Full table data for API responses"""
    id: int
    dining_room_id: int
    
    # Audit fields
    created_by_user_id: int | None = None
    updated_by_user_id: int | None = None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)