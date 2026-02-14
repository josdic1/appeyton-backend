# app/schemas/order.py
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, ConfigDict


class OrderItemCreate(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    reservation_id: int
    items: list[OrderItemCreate]
    notes: str | None = None


class OrderUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None


class OrderResponse(BaseModel):
    id: int
    reservation_id: int
    status: str
    notes: str | None
    meta: dict[str, Any] | None
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