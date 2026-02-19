# app/schemas/daily_stat.py
from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

class DailyStatResponse(BaseModel):
    id: int
    stat_date: date
    dining_room_id: int | None = None
    
    # Reservation Totals
    total_reservations: int
    confirmed_reservations: int
    cancelled_reservations: int
    no_show_reservations: int
    
    # Revenue Metrics
    food_revenue: Decimal
    total_revenue: Decimal
    tax_collected: Decimal
    gratuity_collected: Decimal
    
    # Guest Insights
    total_guests: int
    avg_party_size: Decimal | None = None
    utilization_rate: Decimal | None = None
    
    # JSON Breakdowns
    top_menu_items: List[Dict[str, Any]] | None = None
    peak_hour: str | None = None
    breakdown: Dict[str, Any] | None = None
    
    calculated_at: datetime

    model_config = ConfigDict(from_attributes=True)