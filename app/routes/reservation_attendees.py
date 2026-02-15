# app/routes/reservation_attendees.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.models.member import Member
from app.models.table_entity import TableEntity
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


@router.post("", response_model=ReservationAttendeeResponse, status_code=status.HTTP_201_CREATED)
def create_attendee(
    payload: ReservationAttendeeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """Create attendee - takes reservation_id in the payload body"""
    reservation = _get_owned_reservation(db, payload.reservation_id, user.id)
    
    # Check table capacity
    table = db.query(TableEntity).filter(TableEntity.id == reservation.table_id).first()
    current_attendees = db.query(ReservationAttendee).filter(
        ReservationAttendee.reservation_id == payload.reservation_id
    ).count()
    
    if table and current_attendees >= table.seat_count:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot add attendee: table capacity is {table.seat_count}"
        )

    # If it's a member, fetch their name
    if payload.member_id and not payload.name:
        member = db.query(Member).filter(Member.id == payload.member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        payload.name = member.name

    a = ReservationAttendee(
        reservation_id=payload.reservation_id,
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


@router.get("/reservation/{reservation_id}", response_model=list[ReservationAttendeeResponse])
def list_reservation_attendees(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """Get all attendees for a specific reservation"""
    # Verify reservation exists and user has access
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # Members can only see their own reservations
    if user.role == "member" and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your reservation")
    
    # Staff/admin can see any reservation
    return db.query(ReservationAttendee).filter(
        ReservationAttendee.reservation_id == reservation_id
    ).all()


@router.patch("/{attendee_id}", response_model=ReservationAttendeeResponse)
def update_attendee(
    attendee_id: int,
    payload: ReservationAttendeeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """Update an attendee"""
    a = db.query(ReservationAttendee).filter(ReservationAttendee.id == attendee_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Attendee not found")
    
    # Check ownership
    reservation = db.query(Reservation).filter(Reservation.id == a.reservation_id).first()
    assert reservation is not None  # ← ADDED THIS
    if user.role == "member" and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your reservation")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(a, k, v)

    db.commit()
    db.refresh(a)
    return a


@router.delete("/{attendee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendee(
    attendee_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """Delete an attendee"""
    a = db.query(ReservationAttendee).filter(ReservationAttendee.id == attendee_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Attendee not found")
    
    # Check ownership
    reservation = db.query(Reservation).filter(Reservation.id == a.reservation_id).first()
    assert reservation is not None  # ← ADDED THIS
    if user.role == "member" and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your reservation")

    db.delete(a)
    db.commit()
    return None