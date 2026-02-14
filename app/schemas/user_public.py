# app/schemas/user_public.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any

class UserPublic(BaseModel):
    id: int
    name: str
    role: str
    membership_status: str
    guest_allowance: int
    last_login_at: datetime | None = None
    meta: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)
