# app/schemas/toast.py
from pydantic import BaseModel
from typing import Optional, List, Literal

class ActionButton(BaseModel):
    label: str  # Keep under 20 chars for UI
    action: Literal["retry", "navigate", "dismiss", "reload", "calendar", "download"]
    params: Optional[dict] = None

class ToastResponse(BaseModel):
    status: Literal["loading", "success", "error", "warning"]
    
    # The 5W1H (aim for 8 words each, max 12)
    what: str       
    who: str        
    when: str       
    why: str        
    where: str      
    how: str        
    
    # User actions
    actions: List[ActionButton] = []
    
    # Nerd stats
    meta: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "what": "Table 5 booked for 4 people",
                "who": "Reserved under your name: Jane Smith",
                "when": "Saturday Feb 15, 7:00 PM dinner",
                "why": "All validation passed, payment confirmed",
                "where": "Oak Room, prime dinner hour",
                "how": "Confirmation email sent, add to calendar",
                "actions": [
                    {"label": "Add to Calendar", "action": "calendar", "params": {"reservation_id": 123}},
                    {"label": "View Details", "action": "navigate", "params": {"view": "/reservations/123"}}
                ],
                "meta": {"response_time_ms": 47, "reservation_id": 123}
            }
        }