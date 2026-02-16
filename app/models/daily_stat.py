# app/models/daily_stat.py
from __future__ import annotations
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import Date, DateTime, Numeric, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType


class DailyStat(Base):
    """Daily analytics and statistics for reporting dashboard"""
    __tablename__ = "daily_stats"
    __table_args__ = (
        UniqueConstraint("stat_date", "dining_room_id", name="uq_daily_stat_date_room"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    stat_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    dining_room_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    # If null, this is system-wide stats for the day
    
    # Reservations
    total_reservations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confirmed_reservations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cancelled_reservations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    no_show_reservations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Guests
    total_guests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_party_size: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Revenue
    food_revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    cover_charge_revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    service_fee_revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    tax_collected: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    gratuity_collected: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    total_revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    
    # Orders
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_order_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Table utilization
    total_table_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tables_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    utilization_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    # utilization_rate: 0-100 representing percentage
    
    # Meal breakdown
    breakfast_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lunch_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dinner_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    brunch_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Popular items (top 5)
    top_menu_items: Mapped[list | None] = mapped_column(JSONType, nullable=True)
    # top_menu_items: [{"id": 1, "name": "Ribeye", "count": 25}, ...]
    
    # Peak times
    peak_hour: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # peak_hour: "18:00-19:00"
    
    # Detailed breakdown
    breakdown: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    # breakdown: {"hourly": {...}, "by_meal": {...}, "by_table": {...}}
    
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


# Example Daily Stat:
# stat_date: 2026-02-15
# dining_room_id: 1 (Main Dining Hall)
# total_reservations: 24
# confirmed_reservations: 22
# total_guests: 96
# avg_party_size: 4.0
# food_revenue: $4,500
# total_revenue: $5,800
# utilization_rate: 87.5
# peak_hour: "19:00-20:00"