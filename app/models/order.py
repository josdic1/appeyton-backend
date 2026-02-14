# app/models/order.py
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )

    status: Mapped[str] = mapped_column(String(30), default="incomplete", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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