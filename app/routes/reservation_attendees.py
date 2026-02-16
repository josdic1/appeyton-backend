# app/routes/reservation_attendees.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.member import Member
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.models.table_entity import TableEntity
from app.models.user import User
from app.schemas.reservation_attendee import (
    ReservationAttendeeCreate,
    ReservationAttendeeResponse,
    ReservationAttendeeUpdate,
)
from app.utils.permissions import require_min_role

router = APIRouter()


@router.post("", response_model=ReservationAttendeeResponse, status_code=status.HTTP_201_CREATED)
def create_attendee(
    payload: ReservationAttendeeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """Create attendee (member or guest) with safe, consistent rules.

    Rules enforced (matches your frontend behavior):
    - guest: name is required; member_id must be null
    - member: member_id is required; name is derived from Member.name
    - do not exceed table seat_count
    """
    reservation = db.query(Reservation).filter(Reservation.id == payload.reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if user.role == "member" and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your reservation")

    attendee_type = (payload.attendee_type or "").strip().lower()
    if attendee_type not in {"member", "guest"}:
        raise HTTPException(status_code=400, detail="attendee_type must be 'member' or 'guest'")

    # Enforce table capacity
    table = db.query(TableEntity).filter(TableEntity.id == reservation.table_id).first()
    if table:
        current_attendees = db.query(ReservationAttendee).filter(
            ReservationAttendee.reservation_id == payload.reservation_id
        ).count()
        if current_attendees >= table.seat_count:
            raise HTTPException(
                status_code=409,
                detail=f"TABLE FULL! Seats: {table.seat_count}, Current: {current_attendees}. Choose bigger table.",
            )

    attendee_name: str
    member_id: int | None = None
    dietary = payload.dietary_restrictions

    if attendee_type == "guest":
        raw_name = (payload.name or "").strip()
        if not raw_name:
            raise HTTPException(status_code=400, detail="Guest name required")
        if payload.member_id is not None:
            raise HTTPException(status_code=400, detail="member_id must be null for guest attendees")
        attendee_name = raw_name

    else:  # member
        if not payload.member_id:
            raise HTTPException(status_code=400, detail="member_id is required for member attendees")

        member = db.query(Member).filter(Member.id == payload.member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        # Prevent linking someone else's family member record
        if member.user_id != reservation.user_id:
            raise HTTPException(status_code=403, detail="Member does not belong to reservation owner")

        member_id = member.id
        attendee_name = member.name

        # If not overridden, inherit member dietary restrictions
        if dietary is None and member.dietary_restrictions:
            dietary = member.dietary_restrictions

    attendee = ReservationAttendee(
        reservation_id=payload.reservation_id,
        member_id=member_id,
        name=attendee_name,
        attendee_type=attendee_type,
        dietary_restrictions=dietary,
        meta=payload.meta,
        created_by_user_id=user.id,
    )
    db.add(attendee)
    db.commit()
    db.refresh(attendee)
    return attendee


@router.get("/reservation/{reservation_id}", response_model=list[ReservationAttendeeResponse])
def list_reservation_attendees(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """Get all attendees for a reservation."""
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if user.role == "member" and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your reservation")

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
    """Update attendee safely.

    Requirement: prevent setting name to None on update.
    - If name is None: ignore (do not null it)
    - If name is empty/blank: reject
    - If attendee is a 'member': ignore name updates (name is derived identity)
    """
    attendee = db.query(ReservationAttendee).filter(ReservationAttendee.id == attendee_id).first()
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")

    reservation = db.query(Reservation).filter(Reservation.id == attendee.reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if user.role == "member" and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your reservation")

    data = payload.model_dump(exclude_unset=True)

    # Never allow nulling name (or blanking it)
    if "name" in data:
        proposed = data.get("name")
        if proposed is None:
            # ignore attempt to null name
            data.pop("name", None)
        else:
            proposed = proposed.strip()
            if not proposed:
                raise HTTPException(status_code=400, detail="Name cannot be empty")
            if attendee.attendee_type == "member":
                # member attendee name is derived from Member; ignore updates
                data.pop("name", None)
            else:
                data["name"] = proposed

    for k, v in data.items():
        setattr(attendee, k, v)

    db.commit()
    db.refresh(attendee)
    return attendee


@router.delete("/{attendee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendee(
    attendee_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """Delete attendee."""
    attendee = db.query(ReservationAttendee).filter(ReservationAttendee.id == attendee_id).first()
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")

    reservation = db.query(Reservation).filter(Reservation.id == attendee.reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if user.role == "member" and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your reservation")

    db.delete(attendee)
    db.commit()
    return None
