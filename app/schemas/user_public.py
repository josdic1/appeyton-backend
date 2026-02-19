# app/schemas/user_public.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Any, Dict

class UserPublic(BaseModel):
    """
    Schema for public-facing user data.
    Ensures PII (email, phone, etc.) is never leaked to other users.
    """
    id: int
    name: str = Field(..., max_length=100)
    role: str
    membership_status: str
    guest_allowance: int
    
    # Helpful for "Who's online" or "Recent activity" features
    last_login_at: datetime | None = None
    
    # Optional: common for public profiles
    avatar_url: str | None = None 
    
    # WARNING: Only include if you are certain no private data is in this dict.
    # Consider a validator to strip sensitive keys.
    meta: Dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)