# app/schemas/activity_log.py
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict

class ActivityLogResponse(BaseModel):
    id: int
    user_id: int | None = None
    action: str
    resource_type: str
    resource_id: int | None = None
    details: Dict[str, Any] | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)