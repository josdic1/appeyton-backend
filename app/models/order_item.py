# app/models/order_item.py
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Integer, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    reservation_attendee_id: Mapped[int] = mapped_column(
        ForeignKey("reservation_attendees.id"), nullable=False, index=True
    )
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"), nullable=False, index=True)
    # seat_id: Mapped[int | None] = mapped_column(ForeignKey("seats.id"), nullable=True)

    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    special_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict | None] = mapped_column("metadata", JSONType, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )