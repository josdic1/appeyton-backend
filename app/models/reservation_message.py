# app/models/reservation_message.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.user import User


class ReservationMessage(Base):
    """Messages/chat between staff and members about a reservation"""
    __tablename__ = "reservation_messages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sender_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    message: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), nullable=False, default="text")
    # message_type: "text", "system", "notification", "alert"
    
    is_internal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # is_internal: True = only visible to staff/admin, False = visible to member
    
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    parent_message_id: Mapped[int | None] = mapped_column(
        ForeignKey("reservation_messages.id"),
        nullable=True
    )
    # For threading replies
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    reservation: Mapped["Reservation"] = relationship("Reservation", back_populates="messages")
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_user_id])
    parent: Mapped["ReservationMessage | None"] = relationship(
        "ReservationMessage",
        remote_side=[id],
        backref="replies"
    )


# Example Messages:
# 1. Member: "Can we arrive 15 minutes late?"
# 2. Staff: "Yes, that's fine! We'll hold your table."
# 3. System: "Order confirmed - 4 guests, 6:00 PM"
# 4. Staff (internal): "VIP guest - special attention needed"