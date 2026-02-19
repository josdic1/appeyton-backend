# app/routes/notifications.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.utils.auth import get_current_user
from app.utils import toast_responses

# IMPORTANT:
# main.py provides the prefix: /api/notifications
# So this router MUST NOT add another "/notifications" prefix.
router = APIRouter(tags=["notifications"])


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Efficient endpoint for the Navbar notification badge."""
    count = (
        db.query(func.count(Notification.id))
        .filter(
            Notification.user_id == user.id,
            Notification.read_at.is_(None),
        )
        .scalar()
    )
    return {"count": int(count or 0)}


@router.get("", response_model=List[NotificationResponse])
def get_my_notifications(
    unread_only: bool = True,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the 20 most recent notifications for the logged-in user."""
    q = db.query(Notification).filter(Notification.user_id == user.id)

    if unread_only:
        q = q.filter(Notification.read_at.is_(None))

    return q.order_by(Notification.created_at.desc()).limit(20).all()


@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Mark a specific notification as read by timestamping read_at."""
    notif = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user.id,
        )
        .first()
    )

    if not notif:
        return toast_responses.error_not_found("Notification", notification_id)

    if notif.read_at is None:
        notif.read_at = datetime.now(timezone.utc)
        db.commit()

    return {"status": "ok"}


@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Batch mark all unread notifications as read."""
    now = datetime.now(timezone.utc)

    (
        db.query(Notification)
        .filter(
            Notification.user_id == user.id,
            Notification.read_at.is_(None),
        )
        .update({Notification.read_at: now}, synchronize_session=False)
    )

    db.commit()
    return {"status": "ok", "message": "All notifications marked as read"}
