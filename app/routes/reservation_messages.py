# app/routes/reservation_messages.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
# CRITICAL: Import the CLASS, not just the module
from app.models.reservation_message import ReservationMessage as RMClass
from app.models.reservation import Reservation
from app.models.user import User
from app.schemas.reservation_message import ReservationMessageCreate, ReservationMessageResponse
from app.utils.permissions import get_current_user

router = APIRouter()

@router.get("/{reservation_id}", response_model=list[ReservationMessageResponse])
def get_reservation_chat(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")

    query = db.query(RMClass).options(joinedload(RMClass.sender)).filter(
        RMClass.reservation_id == reservation_id
    )

    if user.role == "member":
        query = query.filter(RMClass.is_internal == False)

    return query.order_by(RMClass.created_at.asc()).all()

@router.post("/{reservation_id}", response_model=ReservationMessageResponse)
def send_reservation_message(
    reservation_id: int,
    payload: ReservationMessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Use the RMClass directly to avoid 'Module not callable'
    message = RMClass(
        reservation_id=reservation_id,
        sender_user_id=user.id,
        message=payload.message,
        is_internal=payload.is_internal if user.role != "member" else False,
    )

    db.add(message)
    db.commit()
    db.refresh(message)
    return message