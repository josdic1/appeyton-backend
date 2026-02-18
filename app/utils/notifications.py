# app/utils/notifications.py
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
    # FIX: Changed types to allow None (str | None)
    resource_type: str | None = None,
    resource_id: int | None = None
):
    """
    Creates a notification in the database.
    In a real app, this would also trigger Email/SMS/Push via background tasks.
    """
    notif = Notification(
        user_id=user_id,
        notification_type=type,
        channel="in_app",
        priority=priority,
        subject=subject,
        message=message,
        resource_type=resource_type,
        resource_id=resource_id,
        status="sent"
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif

def notify_staff(
    db: Session, 
    message: str, 
    # FIX: Changed types to allow None
    resource_type: str | None = None, 
    resource_id: int | None = None
):
    """Send a notification to all staff and admins."""
    staff_members = db.query(User).filter(User.role.in_(["staff", "admin"])).all()
    for staff in staff_members:
        create_notification(
            db, 
            user_id=staff.id, 
            message=message, 
            subject="Staff Alert",
            priority="high",
            resource_type=resource_type,
            resource_id=resource_id
        )