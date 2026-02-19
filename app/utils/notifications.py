# app/utils/notifications.py
from __future__ import annotations
from typing import Any, Dict
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User

def create_notification(
    db: Session,
    user_id: int,
    message: str,
    subject: str = "New Alert",
    type: str = "general",
    priority: str = "normal",
    channel: str = "in_app",
    resource_type: str | None = None,
    resource_id: int | None = None,
    meta: Dict[str, Any] | None = None
):
    """
    Creates a notification in the database context.
    Uses db.flush() instead of commit() to allow the caller to manage the transaction.
    """
    notif = Notification(
        user_id=user_id,
        notification_type=type,
        channel=channel,
        priority=priority,
        subject=subject,
        message=message,
        resource_type=resource_type,
        resource_id=resource_id,
        status="sent" if channel == "in_app" else "queued",
        meta=meta
    )
    db.add(notif)
    db.flush() # Ensure ID is generated without closing transaction
    return notif

def notify_staff(
    db: Session, 
    message: str, 
    resource_type: str | None = None, 
    resource_id: int | None = None,
    subject: str = "Staff Alert"
):
    """
    Sends a notification to all staff and admins.
    Note: For very large staff lists, consider move this to a background task.
    """
    staff_members = db.query(User).filter(User.role.in_(["staff", "admin"])).all()
    
    notifications = []
    for staff in staff_members:
        n = create_notification(
            db, 
            user_id=staff.id, 
            message=message, 
            subject=subject,
            priority="high",
            resource_type=resource_type,
            resource_id=resource_id
        )
        notifications.append(n)
    
    return notifications