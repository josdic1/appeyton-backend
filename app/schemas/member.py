# app/schemas/member.py
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

class MemberBase(BaseModel):
    """Shared fields for Member schemas"""
    name: str = Field(..., min_length=1, max_length=120)
    relation: str | None = Field(None, max_length=60)
    dietary_restrictions: Dict[str, Any] | None = None
    meta: Dict[str, Any] | None = None

class MemberCreate(MemberBase):
    """Schema for creating a new member. 
    user_id is often provided via URL path, but included here for flexibility.
    """
    user_id: int | None = None

class MemberUpdate(BaseModel):
    """All fields optional for PATCH requests"""
    name: str | None = Field(None, min_length=1, max_length=120)
    relation: str | None = Field(None, max_length=60)
    dietary_restrictions: Dict[str, Any] | None = None
    meta: Dict[str, Any] | None = None

class MemberResponse(MemberBase):
    """Full member data for API responses"""
    id: int
    user_id: int
    created_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)