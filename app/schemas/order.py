# app/schemas/order.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class OrderItemCreate(BaseModel):
    """Create an OrderItem directly (used by /api/order-items)."""

    order_id: int
    menu_item_id: int
    reservation_attendee_id: int
    quantity: int = 1
    special_instructions: str | None = None


class OrderItemUpdate(BaseModel):
    quantity: int | None = None
    special_instructions: str | None = None


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    reservation_attendee_id: int
    menu_item_id: int
    quantity: int
    unit_price: Decimal
    special_instructions: str | None
    meta: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    # Added for frontend rendering convenience and to prevent response_model filtering.
    menu_item_name: str | None = None
    attendee_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OrderItemInCreate(BaseModel):
    """For creating items when creating an order."""

    menu_item_id: int
    reservation_attendee_id: int
    quantity: int = 1
    special_instructions: str | None = None


class OrderCreate(BaseModel):
    reservation_id: int
    items: list[OrderItemInCreate]
    notes: str | None = None


class OrderUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None


class OrderResponse(BaseModel):
    id: int
    reservation_id: int
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderWithItemsResponse(BaseModel):
    id: int
    reservation_id: int
    status: str
    notes: str | None
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
