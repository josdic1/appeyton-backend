# app/models/reservation.py
from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import datetime, timezone, date as date_type, time as time_type

from sqlalchemy import (
    Date,
    Time,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.reservation_attendee import ReservationAttendee

try:
    from sqlalchemy.dialects.postgresql import JSONB  # type: ignore
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType  # type: ignore


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        UniqueConstraint("date", "meal_type", "table_id", name="uq_res_date_meal_table"),
        Index("ix_res_room_date", "dining_room_id", "date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    dining_room_id: Mapped[int] = mapped_column(ForeignKey("dining_rooms.id"), nullable=False, index=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("table_entities.id"), nullable=False, index=True)

    date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    meal_type: Mapped[str] = mapped_column(String(30), nullable=False)
    start_time: Mapped[time_type] = mapped_column(Time, nullable=False)
    end_time: Mapped[time_type] = mapped_column(Time, nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict | None] = mapped_column("metadata", JSONType, nullable=True)

    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    cancelled_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    # Relationship to attendees
    attendees: Mapped[list["ReservationAttendee"]] = relationship(
        "ReservationAttendee", 
        back_populates="reservation",
        lazy="select"
    )
    
    @property
    def party_size(self) -> int:
        """Calculate party size from number of attendees"""
        return len(self.attendees)