# app/models/fee.py
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.rule import Rule


class Fee(Base):
    """Actual fees applied to reservations based on rules"""
    __tablename__ = "fees"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    rule_id: Mapped[int | None] = mapped_column(ForeignKey("rules.id"), nullable=True)
    
    fee_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # fee_type: "cover_charge", "tax", "gratuity", "service_fee", "manual"
    
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    is_taxable: Mapped[bool] = mapped_column(nullable=False, default=False)
    applied_to_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    # For percentage fees, track what base amount this was calculated from
    
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    
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
    reservation: Mapped["Reservation"] = relationship("Reservation", back_populates="fees")
    rule: Mapped["Rule"] = relationship("Rule", back_populates="fees")


# Example Fees on a Reservation:
# 1. Cover Charge: fee_type="cover_charge", description="Cover Charge (4 guests)", amount=100.00
# 2. Tax: fee_type="tax", description="Sales Tax (8.5%)", amount=42.50, applied_to_amount=500.00
# 3. Gratuity: fee_type="gratuity", description="Gratuity (20%)", amount=100.00, applied_to_amount=500.00