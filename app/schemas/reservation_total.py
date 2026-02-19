# app/schemas/reservation_total.py
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict

class ReservationTotalResponse(BaseModel):
    id: int
    reservation_id: int
    food_subtotal: Decimal
    cover_charges: Decimal
    service_fees: Decimal
    subtotal_before_tax: Decimal
    tax_amount: Decimal
    subtotal_after_tax: Decimal
    gratuity_amount: Decimal
    total_amount: Decimal
    
    payment_status: str
    amount_paid: Decimal
    balance_due: Decimal
    
    is_locked: bool
    breakdown: Optional[Dict[str, Any]] = None
    calculated_at: datetime

    model_config = ConfigDict(from_attributes=True)