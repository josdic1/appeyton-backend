# app/models/order_item.py
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, Text, DateTime, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .menu_item import MenuItem
    from .order import Order
    from .reservation_attendee import ReservationAttendee

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Added index=True to foreign keys for performance
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_items.id"), 
        nullable=False, 
        index=True
    )
    reservation_attendee_id: Mapped[int] = mapped_column(
        ForeignKey("reservation_attendees.id"), 
        nullable=False, 
        index=True
    )

    quantity: Mapped[int] = mapped_column(Integer, default=1)
    # Correct: Snapshot of the price at time of order
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    special_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    order: Mapped["Order"] = relationship(back_populates="items")
    menu_item: Mapped["MenuItem"] = relationship()
    attendee: Mapped["ReservationAttendee"] = relationship(back_populates="order_items")

    @hybrid_property
    def menu_item_name(self) -> str | None:
        return self.menu_item.name if self.menu_item else None

    @menu_item_name.inplace.expression
    @classmethod
    def _menu_item_name_expression(cls):
        from .menu_item import MenuItem
        return (
            select(MenuItem.name)
            .where(MenuItem.id == cls.menu_item_id)
            .scalar_subquery()
        )

    @hybrid_property
    def attendee_name(self) -> str | None:
        return self.attendee.name if self.attendee else None

    @attendee_name.inplace.expression
    @classmethod
    def _attendee_name_expression(cls):
        from .reservation_attendee import ReservationAttendee
        return (
            select(ReservationAttendee.name)
            .where(ReservationAttendee.id == cls.reservation_attendee_id)
            .scalar_subquery()
        )

    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, item='{self.menu_item_name}', qty={self.quantity})>"