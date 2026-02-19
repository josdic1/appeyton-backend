# app/models/notification.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, Any

from sqlalchemy import String, ForeignKey, DateTime, Text, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User

class Notification(Base):
    """Email/push notifications sent to users"""
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # e.g., "reservation_confirmed", "payment_received"
    
    channel: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    # channel: "email", "sms", "push", "in_app"
    
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default="normal", server_default="normal"
    )
    
    subject: Mapped[str | None] = mapped_column(String(200), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Polymorphic links
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Contact Details
    email_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email_from: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Delivery tracking - added index for worker efficiency
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", server_default="pending", index=True
    )
    
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    
    # Renamed to avoid SQLAlchemy Base attribute confusion
    meta: Mapped[Dict[str, Any] | None] = mapped_column("extra_metadata", JSON, nullable=True)
    
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
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<Notification(user_id={self.user_id}, type='{self.notification_type}', status='{self.status}')>"