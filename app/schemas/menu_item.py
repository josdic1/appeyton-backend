# app/schemas/menu_item.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, List, Dict

from pydantic import BaseModel, ConfigDict, field_validator, Field


def _normalize_dietary_tags(value: Any) -> list[str] | None:
    """Standardizes various inputs into a clean list of strings."""
    if value is None:
        return None
    if isinstance(value, list):
        cleaned = [str(x).strip() for x in value if x is not None and str(x).strip()]
        return cleaned or None
    if isinstance(value, str):
        parts = [p.strip() for p in value.split(",")]
        cleaned = [p for p in parts if p]
        return cleaned or None
    if isinstance(value, dict):
        tags = value.get("tags")
        if isinstance(tags, list):
            return _normalize_dietary_tags(tags)
        if value and all(isinstance(v, bool) for v in value.values()):
            cleaned = [str(k).strip() for k, v in value.items() if v and str(k).strip()]
            return cleaned or None
        cleaned = [str(k).strip() for k in value.keys() if str(k).strip()]
        return cleaned or None
    s = str(value).strip()
    return [s] if s else None


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = None
    category: str = Field(..., min_length=1, max_length=60)
    price: Decimal = Field(..., ge=0)
    is_available: bool = True
    dietary_tags: List[str] | None = None
    display_order: int = 0

    @field_validator("dietary_tags", mode="before")
    @classmethod
    def validate_dietary_tags(cls, v: Any):
        return _normalize_dietary_tags(v)


class MenuItemCreate(MenuItemBase):
    """Used for creating a new menu item"""
    pass


class MenuItemUpdate(BaseModel):
    """All fields optional for PATCH requests"""
    name: str | None = Field(None, min_length=1, max_length=120)
    description: str | None = None
    category: str | None = Field(None, min_length=1, max_length=60)
    price: Decimal | None = Field(None, ge=0)
    is_available: bool | None = None
    dietary_tags: List[str] | None = None
    display_order: int | None = None

    @field_validator("dietary_tags", mode="before")
    @classmethod
    def validate_dietary_tags(cls, v: Any):
        return _normalize_dietary_tags(v)


class MenuItemResponse(MenuItemBase):
    """Standardized response including audit and ID"""
    id: int
    created_by_user_id: int | None = None
    updated_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)