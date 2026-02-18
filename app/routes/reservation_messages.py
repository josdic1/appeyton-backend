# app/routes/reservation_messages.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.reservation_message import ReservationMessage
from app.models.reservation import Reservation
from app.models.user import User
from app.schemas.reservation_message import ReservationMessageCreate, ReservationMessageResponse
from app.utils.permissions import get_current_user
from app.utils.notifications import create_notification, notify_staff

router = APIRouter()

@router.get("/{reservation_id}", response_model=list[ReservationMessageResponse])
def get_messages(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 1. Check access
    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    is_staff = user.role in ["admin", "staff"]
    if not is_staff and res.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 2. Query messages
    query = db.query(ReservationMessage).filter(ReservationMessage.reservation_id == reservation_id)
    
    # Hide internal notes from members
    if not is_staff:
        query = query.filter(ReservationMessage.is_internal == False)
    
    messages = query.order_by(ReservationMessage.created_at.asc()).all()

    # 3. Transform for response (add sender name)
    results = []
    for msg in messages:
        # Simple logic to get name. Ideally done via joinedload(ReservationMessage.sender)
        sender_name = msg.sender.name if msg.sender else "Unknown"
        
        # If staff is viewing, mark member messages as read
        if is_staff and msg.sender_user_id == res.user_id and not msg.is_read:
            msg.is_read = True
            db.add(msg)
            
        results.append({
            "id": msg.id,
            "reservation_id": msg.reservation_id,
            "sender_user_id": msg.sender_user_id,
            "sender_name": sender_name,
            "message": msg.message,
            "message_type": msg.message_type,
            "is_internal": msg.is_internal,
            "is_read": msg.is_read,
            "created_at": msg.created_at
        })
    
    db.commit() # Commit read status updates
    return results


@router.post("/{reservation_id}", response_model=ReservationMessageResponse)
def send_message(
    reservation_id: int,
    payload: ReservationMessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")

    is_staff = user.role in ["admin", "staff"]
    if not is_staff and res.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 1. Create Message
    msg = ReservationMessage(
        reservation_id=reservation_id,
        sender_user_id=user.id,
        message=payload.message,
        is_internal=payload.is_internal if is_staff else False, # Only staff can mark internal
        message_type="text"
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # 2. Trigger Notifications
    # If internal note, don't notify the member
    if not msg.is_internal:
        if is_staff:
            # Staff replied -> Notify Member
            create_notification(
                db,
                user_id=res.user_id,
                message=f"New message from Sterling Catering: {payload.message[:30]}...",
                subject="Reservation Update",
                type="message_received",
                resource_type="reservation",
                resource_id=reservation_id
            )
        else:
            # Member replied -> Notify Staff
            notify_staff(
                db,
                message=f"New message from guest {user.name} (Table {res.table_id or '?'})",
                resource_type="reservation",
                resource_id=reservation_id
            )

    return {
        "id": msg.id,
        "reservation_id": msg.reservation_id,
        "sender_user_id": msg.sender_user_id,
        "sender_name": user.name,
        "message": msg.message,
        "message_type": msg.message_type,
        "is_internal": msg.is_internal,
        "is_read": msg.is_read,
        "created_at": msg.created_at
    }