# app/models/fee.py
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.rule import Rule
    from app.models.user import User

class Fee(Base):
    """Actual fees applied to reservations based on rules"""
    __tablename__ = "fees"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Preserve historical fees even if the logic rule is deleted/retired
    rule_id: Mapped[int | None] = mapped_column(
        ForeignKey("rules.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    fee_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # fee_type: "cover_charge", "tax", "gratuity", "service_fee", "manual"
    
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    is_taxable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # For percentage fees, track what base amount this was calculated from
    applied_to_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Audit Trail
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True
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
    reservation: Mapped["Reservation"] = relationship("Reservation", back_populates="fees")
    rule: Mapped["Rule | None"] = relationship("Rule", back_populates="fees")
    creator: Mapped["User | None"] = relationship("User")

    def __repr__(self) -> str:
        return f"<Fee(type='{self.fee_type}', amount={self.amount})>"