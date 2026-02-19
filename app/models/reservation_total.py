# app/models/reservation_total.py
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict

from sqlalchemy import ForeignKey, DateTime, Numeric, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.user import User

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
    
    # Subtotals - added server_defaults for DB-level safety
    food_subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    cover_charges: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    service_fees: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    
    subtotal_before_tax: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    
    # Tax
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    tax_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    
    subtotal_after_tax: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    
    # Gratuity
    gratuity_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    gratuity_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Final
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    
    # Payment status and balances
    payment_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="unpaid", server_default="unpaid"
    )
    amount_paid: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    balance_due: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    
    # Detailed breakdown for frontend rendering
    breakdown: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    is_locked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Audit trail
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    calculated_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
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
    
    # Relationships
    reservation: Mapped["Reservation"] = relationship("Reservation", back_populates="totals")
    calculator: Mapped["User | None"] = relationship("User")

    def __repr__(self) -> str:
        return f"<ReservationTotal(res_id={self.reservation_id}, total={self.total_amount}, status='{self.payment_status}')>"