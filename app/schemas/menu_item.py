# app/schemas/menu_item.py
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


def _normalize_dietary_tags(value: Any) -> list[str] | None:
    """Normalize dietary_tags into list[str] | None.

    Why this exists:
    - The database JSON column can legally contain either JSON arrays (lists) or
      JSON objects (dicts).
    - Older rows may already store dict-shaped tags.
    - The API contract for the frontend should be stable: list[str] | null.

    Accepted inputs:
    - None -> None
    - list -> list[str]
    - str -> split on commas -> list[str]
    - dict ->
        * {"tags": [...]} -> that list
        * {"vegan": true, "gluten_free": false} -> ["vegan"]
        * otherwise -> keys as tags
    """
    if value is None:
        return None

    if isinstance(value, list):
        cleaned = [str(x).strip() for x in value if x is not None and str(x).strip()]
        return cleaned or None

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        parts = [p.strip() for p in raw.split(",")]
        cleaned = [p for p in parts if p]
        return cleaned or None

    if isinstance(value, dict):
        # Common legacy shape: {"tags": ["vegan", "gf"]}
        tags = value.get("tags")
        if isinstance(tags, list):
            return _normalize_dietary_tags(tags)

        # Common legacy shape: {"vegan": true, "gluten_free": false}
        if value and all(isinstance(v, bool) for v in value.values()):
            cleaned = [str(k).strip() for k, v in value.items() if v and str(k).strip()]
            return cleaned or None

        # Fallback: treat keys as tags
        cleaned = [str(k).strip() for k in value.keys() if str(k).strip()]
        return cleaned or None

    # Best-effort fallback
    s = str(value).strip()
    return [s] if s else None


class MenuItemCreate(BaseModel):
    name: str
    description: str | None = None
    category: str
    price: float
    is_available: bool = True
    dietary_tags: list[str] | None = None
    display_order: int = 0

    @field_validator("dietary_tags", mode="before")
    @classmethod
    def _validate_dietary_tags(cls, v: Any):
        return _normalize_dietary_tags(v)


class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    price: float | None = None
    is_available: bool | None = None
    dietary_tags: list[str] | None = None
    display_order: int | None = None

    @field_validator("dietary_tags", mode="before")
    @classmethod
    def _validate_dietary_tags(cls, v: Any):
        return _normalize_dietary_tags(v)


class MenuItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    category: str
    price: float
    is_available: bool
    dietary_tags: list[str] | None
    display_order: int
    created_by_user_id: int | None
    updated_by_user_id: int | None
    created_at: datetime
    updated_at: datetime

    @field_validator("dietary_tags", mode="before")
    @classmethod
    def _serialize_dietary_tags(cls, v: Any):
        return _normalize_dietary_tags(v)

    model_config = ConfigDict(from_attributes=True)
