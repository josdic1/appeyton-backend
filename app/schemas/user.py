
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Any


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    phone: str | None = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    phone: str | None

    role: str
    membership_status: str
    guest_allowance: int

    created_by_user_id: int | None
    last_login_at: datetime | None
    meta: dict[str, Any] | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
