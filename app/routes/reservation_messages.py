# app/routes/reservation_messages.py
from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.reservation import Reservation
from app.models.reservation_message import ReservationMessage
from app.models.user import User
from app.schemas.reservation_message import (
    ReservationMessageCreate,
    ReservationMessageResponse,
)
from app.utils.auth import get_current_user
from app.utils import toast_responses

# main.py mounts this router at /api/reservation-messages
# so DO NOT add prefix="/reservation-messages" here.
router = APIRouter(tags=["Messages"])


@router.get("/{reservation_id}", response_model=List[ReservationMessageResponse])
def get_reservation_chat(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Fetch message history for a reservation. Members cannot see internal notes."""
    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        return toast_responses.error_not_found("Reservation", reservation_id)

    # Basic ownership check
    if user.role == "member" and res.user_id != user.id:
        return toast_responses.error_forbidden("Chat", "read")

    query = (
        db.query(ReservationMessage)
        .options(joinedload(ReservationMessage.sender))
        .filter(ReservationMessage.reservation_id == reservation_id)
    )

    # Privacy filter: hide staff notes from members
    if user.role == "member":
        query = query.filter(ReservationMessage.is_internal == False)

    return query.order_by(ReservationMessage.created_at.asc()).all()


@router.post("/{reservation_id}", response_model=ReservationMessageResponse)
def send_reservation_message(
    reservation_id: int,
    payload: ReservationMessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send a new message. Staff can mark messages as internal."""
    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        return toast_responses.error_not_found("Reservation", reservation_id)

    # Ownership check
    if user.role == "member" and res.user_id != user.id:
        return toast_responses.error_forbidden("Chat", "send_message")

    # Members can NEVER send internal messages
    is_internal = payload.is_internal if user.role != "member" else False

    message = ReservationMessage(
        reservation_id=reservation_id,
        sender_user_id=user.id,
        message=payload.message,
        is_internal=is_internal,
    )

    try:
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    except Exception as e:
        db.rollback()
        return toast_responses.error_server(f"Failed to send message: {str(e)}")
