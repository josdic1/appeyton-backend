# app/schemas/order.py
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

class OrderItemCreate(BaseModel):
    menu_item_id: int
    reservation_attendee_id: int
    quantity: int = Field(default=1, ge=1)
    special_instructions: Optional[str] = None

class OrderItemUpdate(BaseModel):
    # Allows changing quantity or instructions after the order is in
    quantity: Optional[int] = Field(None, ge=1)
    special_instructions: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    reservation_attendee_id: int
    menu_item_id: int
    quantity: int
    unit_price: Decimal
    special_instructions: Optional[str] = None
    
    # These map to the hybrid_properties in the OrderItem model
    menu_item_name: Optional[str] = None
    attendee_name: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    reservation_id: int
    items: List[OrderItemCreate]
    notes: Optional[str] = None

class OrderUpdate(BaseModel):
    """Schema to handle order status changes and notes updates"""
    status: Optional[str] = None
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    reservation_id: int
    status: str
    notes: Optional[str] = None
    total_price: Decimal # Populated by model hybrid_property
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OrderWithItemsResponse(OrderResponse):
    """Full detail response including all individual line items"""
    items: List[OrderItemResponse]