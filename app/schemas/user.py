# app/schemas/user.py
from __future__ import annotations
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from typing import Any, Dict


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    role: str
    membership_status: str
    guest_allowance: int

    created_by_user_id: int | None = None
    last_login_at: datetime | None = None
    # Note: Using 'meta' to match your model's property name
    meta: Dict[str, Any] | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Fields a user is allowed to change themselves"""
    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)
    phone: str | None = Field(None, max_length=50)


class UserAdminUpdate(UserUpdate):
    """Fields only an admin can change"""
    role: str | None = None
    membership_status: str | None = None
    guest_allowance: int | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

    # CRITICAL FIX: This was missing and caused the 500 error
    model_config = ConfigDict(from_attributes=True)