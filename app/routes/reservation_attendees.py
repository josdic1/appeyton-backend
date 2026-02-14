# app/routes/reservation_attendees.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.schemas.reservation_attendee import (
    ReservationAttendeeCreate,
    ReservationAttendeeUpdate,
    ReservationAttendeeResponse,
)
from app.utils.permissions import require_min_role
from app.models.user import User

router = APIRouter()


def _get_owned_reservation(db: Session, reservation_id: int, user_id: int) -> Reservation:
    """Helper to ensure member can only access their own reservations"""
    r = db.query(Reservation).filter(Reservation.id == reservation_id, Reservation.user_id == user_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return r


@router.post("/{reservation_id}/attendees", response_model=ReservationAttendeeResponse, status_code=status.HTTP_201_CREATED)
def create_attendee(
    reservation_id: int,
    payload: ReservationAttendeeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    _get_owned_reservation(db, reservation_id, user.id)

    a = ReservationAttendee(
        reservation_id=reservation_id,
        member_id=payload.member_id,
        name=payload.name,
        attendee_type=payload.attendee_type,
        dietary_restrictions=payload.dietary_restrictions,
        meta=payload.meta,
        created_by_user_id=user.id,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.get("/{reservation_id}/attendees", response_model=list[ReservationAttendeeResponse])
def list_attendees(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    _get_owned_reservation(db, reservation_id, user.id)
    return db.query(ReservationAttendee).filter(ReservationAttendee.reservation_id == reservation_id).all()


@router.patch("/{reservation_id}/attendees/{attendee_id}", response_model=ReservationAttendeeResponse)
def update_attendee(
    reservation_id: int,
    attendee_id: int,
    payload: ReservationAttendeeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    _get_owned_reservation(db, reservation_id, user.id)

    a = db.query(ReservationAttendee).filter(
        ReservationAttendee.id == attendee_id,
        ReservationAttendee.reservation_id == reservation_id,
    ).first()
    if not a:
        raise HTTPException(status_code=404, detail="Attendee not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(a, k, v)

    db.commit()
    db.refresh(a)
    return a


@router.delete("/{reservation_id}/attendees/{attendee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendee(
    reservation_id: int,
    attendee_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    _get_owned_reservation(db, reservation_id, user.id)

    a = db.query(ReservationAttendee).filter(
        ReservationAttendee.id == attendee_id,
        ReservationAttendee.reservation_id == reservation_id,
    ).first()
    if not a:
        raise HTTPException(status_code=404, detail="Attendee not found")

    db.delete(a)
    db.commit()
    return None