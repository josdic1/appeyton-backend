# app/models/reservation_attendee.py
from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, DateTime, String, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.order_item import OrderItem
    from app.models.member import Member
    from app.models.seat import Seat
    from app.models.user import User

class ReservationAttendee(Base):
    __tablename__ = "reservation_attendees"

    id: Mapped[int] = mapped_column(primary_key=True)

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    member_id: Mapped[int | None] = mapped_column(
        ForeignKey("members.id"),
        nullable=True,
        index=True,
    )

    seat_id: Mapped[int | None] = mapped_column(
        ForeignKey("seats.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)

    attendee_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="guest",
        server_default="guest",
    )

    dietary_restrictions: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    reservation: Mapped["Reservation"] = relationship("Reservation", back_populates="attendees")
    member: Mapped["Member | None"] = relationship("Member")
    seat: Mapped["Seat | None"] = relationship("Seat")
    
    # Explicitly mapping creator
    creator: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_user_id])

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="attendee",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ReservationAttendee(name='{self.name}', type='{self.attendee_type}')>"