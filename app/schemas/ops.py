# app/schemas/ops.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class UserOpsResponse(BaseModel):
    """Lean schema for administrative list views"""
    id: int
    name: str
    email: EmailStr # Essential for search/identification
    role: str
    membership_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)