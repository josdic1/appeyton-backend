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
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict | None] = mapped_column("metadata", JSONType, nullable=True)
 
    order: Mapped["Order"] = relationship("Order", back_populates="reservation", uselist=False)
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

    # Relationships
    attendees: Mapped[list["ReservationAttendee"]] = relationship(
        "ReservationAttendee",
        back_populates="reservation",
        cascade="all, delete-orphan",
        lazy="selectin"  # This loads attendees automatically for party_size
    )

    # NEW: Fees and totals
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

    # NEW: Messages
    messages: Mapped[list["ReservationMessage"]] = relationship(
        "ReservationMessage",
        back_populates="reservation",
        cascade="all, delete-orphan",
        order_by="ReservationMessage.created_at"
    )

    # Computed properties
    @property
    def party_size(self) -> int:
        """Computed from number of attendees"""
        return len(self.attendees)

    @party_size.setter
    def party_size(self, _value: int | None) -> None:
        """No-op setter.

        `party_size` is computed from attendees.

        Some create/update code paths still include `party_size` in payloads.
        Without a setter, assigning to a @property raises AttributeError.
        This setter intentionally ignores assignments to keep the computed
        behavior while preventing crashes.
        """
        return

    @property
    def total_amount(self) -> Decimal:
        """Get total amount from ReservationTotal if exists"""
        if self.totals:
            return self.totals.total_amount
        return Decimal("0.00")

    @property
    def payment_status(self) -> str:
        """Get payment status from ReservationTotal if exists"""
        if self.totals:
            return self.totals.payment_status
        return "unpaid"
