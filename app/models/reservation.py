# app/models/reservation.py
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timezone, date as date_type, time as time_type
from decimal import Decimal

from sqlalchemy import Integer, String, ForeignKey, DateTime, Date, Time, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.reservation_attendee import ReservationAttendee
    from app.models.fee import Fee
    from app.models.reservation_total import ReservationTotal
    from app.models.reservation_message import ReservationMessage
    from app.models.order import Order
    from app.models.dining_room import DiningRoom
    from app.models.table_entity import TableEntity

try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        Index("ix_reservations_date_meal_table", "date", "meal_type", "table_id", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    dining_room_id: Mapped[int] = mapped_column(ForeignKey("dining_rooms.id"), nullable=False, index=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("table_entities.id"), nullable=False, index=True)

    date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    meal_type: Mapped[str] = mapped_column(String(30), nullable=False)
    start_time: Mapped[time_type] = mapped_column(Time, nullable=False)
    end_time: Mapped[time_type] = mapped_column(Time, nullable=False)

    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False, index=True)
    
    # ── THE KITCHEN TRACKER (FIXES 500 ERROR) ──
    fired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

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

    # ── RELATIONSHIPS ──
    dining_room: Mapped["DiningRoom"] = relationship("DiningRoom")
    table: Mapped["TableEntity"] = relationship("TableEntity")
    order: Mapped["Order"] = relationship("Order", back_populates="reservation", uselist=False)

    attendees: Mapped[list["ReservationAttendee"]] = relationship(
        "ReservationAttendee",
        back_populates="reservation",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    fees: Mapped[list["Fee"]] = relationship(
        "Fee",
        back_populates="reservation",
        cascade="all, delete-orphan"
    )

    totals: Mapped["ReservationTotal | None"] = relationship(
        "ReservationTotal",
        back_populates="reservation",
        uselist=False,
        cascade="all, delete-orphan"
    )

    messages: Mapped[list["ReservationMessage"]] = relationship(
        "ReservationMessage",
        back_populates="reservation",
        cascade="all, delete-orphan",
        order_by="ReservationMessage.created_at"
    )

    # ── COMPUTED PROPERTIES ──
    @property
    def party_size(self) -> int:
        return len(self.attendees)

    @property
    def total_amount(self) -> Decimal:
        if self.totals:
            return self.totals.total_amount
        return Decimal("0.00")

    @property
    def payment_status(self) -> str:
        if self.totals:
            return self.totals.payment_status
        return "unpaid"