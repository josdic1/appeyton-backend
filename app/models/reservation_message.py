# app/models/reservation_message.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

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
    
    # e.g., "text", "image", "system_alert"
    message_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="text", server_default="text"
    )
    
    # If True, only staff/admins can see this message
    is_internal: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    
    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Self-referential ID for threaded replies
    parent_message_id: Mapped[int | None] = mapped_column(
        ForeignKey("reservation_messages.id", ondelete="CASCADE"), 
        nullable=True
    )
    
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
    
    # Self-referential relationships for threading
    parent: Mapped["ReservationMessage | None"] = relationship(
        "ReservationMessage", 
        remote_side=[id], 
        back_populates="replies"
    )
    replies: Mapped[List["ReservationMessage"]] = relationship(
        "ReservationMessage", 
        back_populates="parent",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        internal_flag = " [INTERNAL]" if self.is_internal else ""
        return f"<ReservationMessage(id={self.id}, sender={self.sender_user_id}{internal_flag})>"