# app/schemas/seat.py
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Any, Optional

class SeatBase(BaseModel):
    # Ensure seat numbers are physically realistic
    seat_number: int = Field(..., ge=1)
    position: Optional[str] = Field(None, max_length=50) # e.g., "Wall", "Aisle"
    is_accessible: bool = False
    is_available: bool = True
    preferences: Optional[dict[str, Any]] = None
    notes: Optional[str] = None
    table_id: int

class SeatCreate(SeatBase):
    """Schema for creating a new seat"""
    pass

class SeatUpdate(BaseModel):
    """Schema for updating an existing seat (all fields optional)"""
    seat_number: Optional[int] = Field(None, ge=1)
    position: Optional[str] = Field(None, max_length=50)
    is_accessible: Optional[bool] = None
    is_available: Optional[bool] = None
    preferences: Optional[dict[str, Any]] = None
    notes: Optional[str] = None
    # table_id is optional here; moving a seat to a different table is possible 
    # but usually requires updating the seat_number to avoid unique constraint violations.
    table_id: Optional[int] = None

class SeatResponse(SeatBase):
    """Schema for returning seat data to the frontend"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_user_id: Optional[int] = None
    updated_by_user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)