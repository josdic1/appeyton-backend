# app/schemas/ops.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserOpsResponse(BaseModel):
    id: int
    name: str
    role: str
    membership_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
