# app/models/order_item.py
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal 
from typing import TYPE_CHECKING
from sqlalchemy import Integer, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.reservation_attendee import ReservationAttendee
    from app.models.order import Order
    from app.models.menu_item import MenuItem

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ── THE GUEST LINK ──
    reservation_attendee_id: Mapped[int] = mapped_column(
        ForeignKey("reservation_attendees.id", ondelete="CASCADE"), 
        nullable=False, index=True
    )
    
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    special_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    menu_item: Mapped["MenuItem"] = relationship("MenuItem")
    attendee: Mapped["ReservationAttendee"] = relationship("ReservationAttendee", back_populates="order_items")