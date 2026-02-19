# app/schemas/toast.py
from __future__ import annotations
from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

class ActionButton(BaseModel):
    # Enforces the UI rule mentioned in your comment
    label: str = Field(..., max_length=20)  
    action: Literal["retry", "navigate", "dismiss", "reload", "calendar", "download"]
    params: Optional[Dict[str, Any]] = None

class ToastResponse(BaseModel):
    status: Literal["loading", "success", "error", "warning"]
    
    # The 5W1H (Brief, informative headers)
    what: str = Field(..., max_length=100)
    who: str = Field(..., max_length=100)
    when: str = Field(..., max_length=100)
    why: str = Field(..., max_length=100)
    where: str = Field(..., max_length=100)
    how: str = Field(..., max_length=100)
    
    # User actions
    actions: List[ActionButton] = Field(default_factory=list)
    
    # Audit/Nerd stats
    meta: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "what": "Table 5 booked for 4 people",
                "who": "Reserved under your name: Jane Smith",
                "when": "Saturday Feb 15, 7:00 PM dinner",
                "why": "All validation passed, payment confirmed",
                "where": "Oak Room, prime dinner hour",
                "how": "Confirmation email sent, add to calendar",
                "actions": [
                    {"label": "Add to Calendar", "action": "calendar", "params": {"id": 123}},
                    {"label": "View Details", "action": "navigate", "params": {"path": "/res/123"}}
                ],
                "meta": {"response_time_ms": 47}
            }
        }
    )