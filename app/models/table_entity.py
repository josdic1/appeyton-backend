# app/models/table_entity.py
# CRITICAL FIX: Removed @event.listens_for auto_generate_seats.
# admin_tables.py route handles seat creation manually after flush().
# Having BOTH caused every new table to get double the expected seats.
from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from sqlalchemy import String, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.dining_room import DiningRoom
    from app.models.seat import Seat

try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType

class TableEntity(Base):
    __tablename__ = "table_entities"
    __table_args__ = (
        UniqueConstraint("dining_room_id", "table_number", name="uq_dining_room_table_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dining_room_id: Mapped[int] = mapped_column(ForeignKey("dining_rooms.id"), nullable=False, index=True)
    table_number: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_count: Mapped[int] = mapped_column(Integer, nullable=False)
    position_x: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_y: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
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

    dining_room: Mapped["DiningRoom"] = relationship("DiningRoom", back_populates="tables")
    seats: Mapped[List["Seat"]] = relationship(
        "Seat", back_populates="table",
        cascade="all, delete-orphan",
        order_by="Seat.seat_number"
    )