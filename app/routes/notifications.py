# app/routes/notifications.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.utils.permissions import get_current_user

router = APIRouter()

@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Highly efficient endpoint for the Navbar notification dot.
    Returns only the integer count of unread notifications.
    """
    count = db.query(func.count(Notification.id)).filter(
        Notification.user_id == user.id,
        Notification.read_at == None
    ).scalar()
    
    return {"count": count or 0}

@router.get("", response_model=list[NotificationResponse])
def get_my_notifications(
    unread_only: bool = True,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get recent notifications for the logged-in user."""
    query = db.query(Notification).filter(Notification.user_id == user.id)
    
    if unread_only:
        query = query.filter(Notification.read_at == None) #
        
    return query.order_by(Notification.created_at.desc()).limit(20).all() #

@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Mark a specific notification as read by timestamping read_at."""
    notif = db.query(Notification).filter(
        Notification.id == notification_id, 
        Notification.user_id == user.id
    ).first() #
    
    if not notif:
        raise HTTPException(404, "Notification not found") #
        
    from datetime import datetime, timezone
    notif.read_at = datetime.now(timezone.utc) #
    db.commit() #
    return {"status": "ok"}