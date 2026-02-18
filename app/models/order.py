# app/models/order.py
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, ForeignKey, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.database import Base

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.order_item import OrderItem

try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True, 
        unique=True
    )

    # ── RELATIONSHIPS ──
    reservation: Mapped["Reservation"] = relationship("Reservation", back_populates="order")
    
    # Cascade ensures that deleting an order cleans up all individual meal items
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", 
        back_populates="order", 
        cascade="all, delete-orphan"
    )

    status: Mapped[str] = mapped_column(String(30), default="incomplete", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict | None] = mapped_column("metadata", JSONType, nullable=True)

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

    # ── DYNAMIC CALCULATION ──
    @hybrid_property
    def total_price(self) -> Decimal:
        """Calculates the sum of (quantity * unit_price) for all items in the order."""
        return sum((item.quantity * item.unit_price for item in self.items), Decimal("0.00"))

    @total_price.inplace.expression
    @classmethod
    def _total_price_expression(cls):
        """Allows the database to filter or sort by total_price efficiently."""
        from app.models.order_item import OrderItem
        return (
            select(func.sum(OrderItem.quantity * OrderItem.unit_price))
            .where(OrderItem.order_id == cls.id)
            .correlate_except(OrderItem)
            .as_scalar()
        )