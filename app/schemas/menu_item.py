# app/schemas/menu_item.py
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class MenuItemCreate(BaseModel):
    name: str
    description: str | None = None
    category: str
    price: Decimal
    is_available: bool = True
    dietary_tags: dict[str, Any] | None = None
    display_order: int = 0


class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    price: Decimal | None = None
    is_available: bool | None = None
    dietary_tags: dict[str, Any] | None = None
    display_order: int | None = None


class MenuItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    category: str
    price: Decimal
    is_available: bool
    dietary_tags: dict[str, Any] | None
    display_order: int
    created_by_user_id: int | None
    updated_by_user_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)