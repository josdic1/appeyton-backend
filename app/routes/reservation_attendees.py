# app/routes/reservation_attendees.py
# ADDED: POST endpoint — was missing, only GET and PATCH existed.
# Without this, the frontend cannot create attendees after booking.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.schemas.reservation_attendee import (
    ReservationAttendeeCreate,
    ReservationAttendeeResponse,
    ReservationAttendeeUpdate,
)
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission

router = APIRouter()


@router.post("", response_model=ReservationAttendeeResponse, status_code=status.HTTP_201_CREATED)
def create_attendee(
    payload: ReservationAttendeeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("ReservationAttendee", "write")),
):
    """Add an attendee to an existing reservation.
    
    Members can only add attendees to their own reservations.
    Staff/admin can add to any reservation.
    """
    reservation = db.query(Reservation).filter(Reservation.id == payload.reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Ownership check for members
    if scope == "own" and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Cannot add attendees to another member's reservation")

    # Guard against overfilling the table
    from app.models.table_entity import TableEntity
    table = db.query(TableEntity).filter(TableEntity.id == reservation.table_id).first()
    if table:
        current_count = len(reservation.attendees)
        if current_count >= table.seat_count:
            raise HTTPException(
                status_code=409,
                detail=f"Table {table.table_number} is already at capacity ({table.seat_count} seats)"
            )

    attendee = ReservationAttendee(
        **payload.model_dump(),
        created_by_user_id=user.id,
    )
    db.add(attendee)
    db.commit()
    db.refresh(attendee)
    return attendee


@router.get("", response_model=List[ReservationAttendeeResponse])
def list_attendees(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Reservation", "read")),
):
    query = db.query(ReservationAttendee)
    if scope == "own":
        query = query.join(Reservation).filter(Reservation.user_id == user.id)
    return query.all()


@router.patch("/{attendee_id}", response_model=ReservationAttendeeResponse)
def update_attendee(
    attendee_id: int,
    payload: ReservationAttendeeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Reservation", "write")),
):
    attendee = db.query(ReservationAttendee).filter(ReservationAttendee.id == attendee_id).first()
    if not attendee:
        raise HTTPException(404, "Attendee not found")

    res = db.query(Reservation).filter(Reservation.id == attendee.reservation_id).first()
    if not res:
        raise HTTPException(404, "Reservation missing")
    if scope == "own" and res.user_id != user.id:
        raise HTTPException(403)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(attendee, key, value)

    db.commit()
    db.refresh(attendee)
    return attendee


@router.delete("/{attendee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendee(
    attendee_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("ReservationAttendee", "delete")),
):
    attendee = db.query(ReservationAttendee).filter(ReservationAttendee.id == attendee_id).first()
    if not attendee:
        raise HTTPException(404, "Attendee not found")

    res = db.query(Reservation).filter(Reservation.id == attendee.reservation_id).first()
    if scope == "own" and res and res.user_id != user.id:
        raise HTTPException(403)

    db.delete(attendee)
    db.commit()
    return None