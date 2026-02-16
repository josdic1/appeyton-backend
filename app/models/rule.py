# app/models/rule.py
from __future__ import annotations
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Boolean, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.fee import Fee

try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType


class Rule(Base):
    """Define pricing rules: cover charges, taxes, gratuity, fees"""
    __tablename__ = "rules"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # rule_type: "cover_charge", "tax", "gratuity", "service_fee", "cancellation_fee"
    
    amount_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # amount_type: "fixed", "percentage", "per_person"
    
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    # If percentage: 18.5 = 18.5%
    # If fixed: 50.00 = $50
    # If per_person: 25.00 = $25 per person
    
    applies_to: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # applies_to: "all", "dinner", "brunch", "private_room"
    
    min_party_size: Mapped[int | None] = mapped_column(nullable=True)
    max_party_size: Mapped[int | None] = mapped_column(nullable=True)
    
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_taxable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    conditions: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    # conditions: {"day_of_week": ["friday", "saturday"], "meal_type": "dinner"}
    
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
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
    fees: Mapped[list["Fee"]] = relationship("Fee", back_populates="rule")


# Example Rules:
# 1. Cover Charge: type="cover_charge", amount_type="per_person", amount=25.00
# 2. Tax: type="tax", amount_type="percentage", amount=8.5, applies_to="all"
# 3. Gratuity: type="gratuity", amount_type="percentage", amount=20.0, min_party_size=6
# 4. Service Fee: type="service_fee", amount_type="fixed", amount=50.00, applies_to="private_room"