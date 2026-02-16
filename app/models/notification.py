# app/models/notification.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Text, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User

try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONType = JSONB
except Exception:
    from sqlalchemy import JSON as JSONType


class Notification(Base):
    """Email/push notifications sent to users"""
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # notification_type: "reservation_confirmed", "reservation_reminder", 
    #                    "order_ready", "payment_received", "message_received"
    
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    # channel: "email", "sms", "push", "in_app"
    
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")
    # priority: "low", "normal", "high", "urgent"
    
    subject: Mapped[str | None] = mapped_column(String(200), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Links to related resources
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # resource_type: "reservation", "order", "message"
    
    # Email specific
    email_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email_from: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Delivery tracking
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    # status: "pending", "sent", "delivered", "failed", "read"
    
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    metadata_json: Mapped[dict | None] = mapped_column("metadata_json", JSONType, nullable=True)
    # metadata_json: {"template_id": "...", "variables": {...}}
    
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


# Example Notifications:
# 1. Confirmation: "Your reservation is confirmed for Friday, 6:00 PM"
# 2. Reminder: "Reminder: Your reservation is tomorrow at 6:00 PM"
# 3. Order Ready: "Your order is ready for pickup"
# 4. Message: "You have a new message about your reservation"