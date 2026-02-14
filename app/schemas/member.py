from __future__ import annotations
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

class MemberCreate(BaseModel):
    name: str
    relation: str | None = None
    dietary_restrictions: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None

class MemberUpdate(BaseModel):
    name: str | None = None
    relation: str | None = None
    dietary_restrictions: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None

class MemberResponse(BaseModel):
    id: int
    user_id: int
    created_by_user_id: int | None
    name: str
    relation: str | None
    dietary_restrictions: dict[str, Any] | None
    meta: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
