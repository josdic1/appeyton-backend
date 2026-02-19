# app/models/rule.py
from __future__ import annotations
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import TYPE_CHECKING, List, Dict, Any

from sqlalchemy import String, ForeignKey, DateTime, Boolean, Date, Numeric, JSON, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.fee import Fee
    from app.models.user import User

class Rule(Base):
    """Define pricing rules: cover charges, taxes, gratuity, fees"""
    __tablename__ = "rules"
    __table_args__ = (
        CheckConstraint(
            "min_party_size <= max_party_size", 
            name="ck_rule_party_size_range"
        ),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # e.g., "cover_charge", "tax", "gratuity"
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # e.g., "fixed", "percentage", "per_person"
    amount_type: Mapped[str] = mapped_column(String(20), nullable=False)
    
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    applies_to: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    min_party_size: Mapped[int | None] = mapped_column(nullable=True)
    max_party_size: Mapped[int | None] = mapped_column(nullable=True)
    
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    is_taxable: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    
    # Standardized JSON
    conditions: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    display_order: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Audit Trail
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    
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
    fees: Mapped[List["Fee"]] = relationship("Fee", back_populates="rule")
    creator: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_user_id])
    updater: Mapped["User | None"] = relationship("User", foreign_keys=[updated_by_user_id])

    def __repr__(self) -> str:
        return f"<Rule(name='{self.name}', type='{self.rule_type}', amount={self.amount})>"