# app/models/order.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, String, Text, DateTime, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .reservation import Reservation
    from .order_item import OrderItem

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False
    )
    
    status: Mapped[str] = mapped_column(String(30), default="incomplete", server_default="incomplete")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    reservation: Mapped["Reservation"] = relationship(back_populates="order")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", 
        back_populates="order", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    @hybrid_property
    def total_price(self) -> Decimal:
        """Calculates total price in Python using Decimal to avoid rounding errors."""
        # Explicitly starting sum with a Decimal to fix Pylance reportReturnType error
        return sum(
            (item.unit_price * item.quantity for item in self.items), 
            Decimal("0.00")
        )

    @total_price.inplace.expression
    @classmethod
    def _total_price_expression(cls):
        """Allows SQL-side math for filtering and sorting by order total."""
        from .order_item import OrderItem
        return (
            select(func.sum(OrderItem.unit_price * OrderItem.quantity))
            .where(OrderItem.order_id == cls.id)
            .label("total_price")
            .scalar_subquery()
        )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, status='{self.status}', total={self.total_price})>"