# app/models/daily_stat.py
from __future__ import annotations
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, List, Dict, Any

from sqlalchemy import Date, DateTime, Numeric, Integer, String, UniqueConstraint, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from .dining_room import DiningRoom

class DailyStat(Base):
    """Daily analytics and statistics for reporting dashboard"""
    __tablename__ = "daily_stats"
    __table_args__ = (
        UniqueConstraint("stat_date", "dining_room_id", name="uq_daily_stat_date_room"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    stat_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Added formal ForeignKey to DiningRoom
    dining_room_id: Mapped[int | None] = mapped_column(
        ForeignKey("dining_rooms.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    
    # Reservations
    total_reservations: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    confirmed_reservations: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    cancelled_reservations: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    no_show_reservations: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    
    # Guests
    total_guests: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    avg_party_size: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Revenue (Numeric for financial precision)
    food_revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0.00")
    cover_charge_revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0.00")
    service_fee_revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0.00")
    tax_collected: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0.00")
    gratuity_collected: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0.00")
    total_revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0.00")
    
    # Orders
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    avg_order_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Table utilization
    total_table_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    tables_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    utilization_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Meal breakdown
    breakfast_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    lunch_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    dinner_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    brunch_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    
    # JSON Blobs for complex data
    top_menu_items: Mapped[List[Dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    peak_hour: Mapped[str | None] = mapped_column(String(20), nullable=True)
    breakdown: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Audit Trail
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
        nullable=False,
    )

    # Relationships
    dining_room: Mapped["DiningRoom | None"] = relationship("DiningRoom")

    def __repr__(self) -> str:
        scope = f"Room {self.dining_room_id}" if self.dining_room_id else "Global"
        return f"<DailyStat(date={self.stat_date}, scope={scope}, rev={self.total_revenue})>"