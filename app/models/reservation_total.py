# app/models/reservation_total.py
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, DateTime, Numeric, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.reservation import Reservation

try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType


class ReservationTotal(Base):
    """Calculated total bill for a reservation with breakdown"""
    __tablename__ = "reservation_totals"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Subtotals
    food_subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    cover_charges: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    service_fees: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    
    # Before tax
    subtotal_before_tax: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    
    # Tax
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    tax_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    
    # After tax
    subtotal_after_tax: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    
    # Gratuity
    gratuity_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    gratuity_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Final
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    
    # Payment
    payment_status: Mapped[str] = mapped_column(String(20), nullable=False, default="unpaid")
    # payment_status: "unpaid", "partial", "paid", "refunded"
    
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    balance_due: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    
    # Breakdown for display
    breakdown: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    # breakdown: {
    #   "items": [...],
    #   "fees": [...],
    #   "taxes": [...],
    #   "tip": {...}
    # }
    
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Lock totals after payment to prevent changes
    
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    calculated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    
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
    
    # Relationships
    reservation: Mapped["Reservation"] = relationship("Reservation", back_populates="totals")


# Example Calculation:
# food_subtotal: $500.00 (from order items)
# cover_charges: $100.00 (4 guests × $25)
# service_fees: $50.00 (private room fee)
# subtotal_before_tax: $650.00
# tax_amount: $55.25 (8.5% of $650)
# subtotal_after_tax: $705.25
# gratuity_amount: $130.00 (20% of $650)
# total_amount: $835.25