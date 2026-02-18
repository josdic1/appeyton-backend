# app/routes/notifications.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.utils.permissions import get_current_user

router = APIRouter()

@router.get("", response_model=list[NotificationResponse])
def get_my_notifications(
    unread_only: bool = True,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get notifications for the logged-in user."""
    query = db.query(Notification).filter(Notification.user_id == user.id)
    
    if unread_only:
        # Show unread + recently read (last 5 mins) if you wanted, 
        # but simpler is just unread or everything.
        # Let's return unread ones primarily.
        query = query.filter(Notification.read_at == None)
        
    return query.order_by(Notification.created_at.desc()).limit(20).all()

@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    notif = db.query(Notification).filter(
        Notification.id == notification_id, 
        Notification.user_id == user.id
    ).first()
    
    if not notif:
        raise HTTPException(404, "Notification not found")
        
    from datetime import datetime, timezone
    notif.read_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "ok"}