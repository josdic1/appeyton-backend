from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.schemas.reservation_attendee import ReservationAttendeeCreate, ReservationAttendeeResponse
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission

router = APIRouter()

@router.post("", response_model=ReservationAttendeeResponse, status_code=201)
def create_attendee(
    payload: ReservationAttendeeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Reservation", "write")),
):
    res = db.query(Reservation).filter(Reservation.id == payload.reservation_id).first()
    if not res: raise HTTPException(404)
    
    if scope == "own" and res.user_id != user.id:
        raise HTTPException(403, "Not your reservation")

    attendee = ReservationAttendee(**payload.model_dump(), created_by_user_id=user.id)
    db.add(attendee)
    db.commit()
    return attendee