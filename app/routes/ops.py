# app/routes/ops.py
from __future__ import annotations

from datetime import date as date_type
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.models.user import User
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.models.table_entity import TableEntity
from app.models.seat import Seat

from app.utils.auth import get_current_user
from app.utils.permissions import get_permission
from app.utils import toast_responses

from app.schemas.user_public import UserPublic
from app.schemas.reservation import ReservationResponse
from app.schemas.reservation_attendee import (
    ReservationAttendeeResponse,
    ReservationAttendeeSyncList,
)
from app.schemas.table_entity import TableEntityResponse
from app.schemas.seat import SeatResponse

# IMPORTANT:
# main.py already mounts this router at /api/ops
# so DO NOT add prefix="/ops" here, or you'll get /api/ops/ops/...
router = APIRouter(tags=["Operations"])


# ── FLOOR PLAN DATA (what your frontend is calling) ──────────────────

@router.get("/tables", response_model=List[TableEntityResponse])
def ops_list_tables(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Table", "read")),
):
    """
    Staff floorplan needs tables.
    Frontend calls: GET /api/ops/tables
    """
    if scope != "all":
        return toast_responses.error_forbidden("Table", "read_all")

    # Order by something stable
    q = db.query(TableEntity)
    # If these columns exist in your model (they usually do), keep them:
    if hasattr(TableEntity, "dining_room_id") and hasattr(TableEntity, "table_number"):
        q = q.order_by(TableEntity.dining_room_id.asc(), TableEntity.table_number.asc())
    else:
        q = q.order_by(TableEntity.id.asc())

    return q.all()


@router.get("/seats", response_model=List[SeatResponse])
def ops_list_seats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Seat", "read")),
):
    """
    Staff floorplan needs seats.
    Frontend calls: GET /api/ops/seats
    """
    if scope != "all":
        return toast_responses.error_forbidden("Seat", "read_all")

    q = db.query(Seat)
    # Order by table then seat number if available, otherwise by id
    if hasattr(Seat, "table_id") and hasattr(Seat, "seat_number"):
        q = q.order_by(Seat.table_id.asc(), Seat.seat_number.asc())
    else:
        q = q.order_by(Seat.id.asc())

    return q.all()


@router.get("/reservations", response_model=List[ReservationResponse])
def ops_list_reservations(
    date: str | None = Query(None, description="YYYY-MM-DD"),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Reservation", "read")),
):
    """
    Staff view for managing all bookings.
    Frontend calls: GET /api/ops/reservations?date=YYYY-MM-DD
    """
    if scope != "all":
        return toast_responses.error_forbidden("Reservation", "read_all")

    q = db.query(Reservation).options(
        joinedload(Reservation.table),
        selectinload(Reservation.attendees),
    )

    if status:
        q = q.filter(Reservation.status == status)

    if date:
        try:
            parsed_date = date_type.fromisoformat(date)
            q = q.filter(Reservation.date == parsed_date)
        except ValueError:
            return toast_responses.error_validation("date", "Invalid date format", "Use YYYY-MM-DD")

    return q.order_by(Reservation.date.desc(), Reservation.start_time.asc()).all()


# ── SYNC LOGIC (Manifest Reconciliation) ─────────────────────────────

@router.patch(
    "/reservations/{reservation_id}/attendees/sync",
    response_model=List[ReservationAttendeeResponse],
)
def ops_sync_attendees(
    reservation_id: int,
    payload: ReservationAttendeeSyncList,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("ReservationAttendee", "write")),
):
    """Staff only: Reconciles the guest manifest (Add/Update/Delete)."""
    if scope != "all":
        return toast_responses.error_forbidden("ReservationAttendee", "sync")

    res = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not res:
        return toast_responses.error_not_found("Reservation", reservation_id)

    existing_guests = (
        db.query(ReservationAttendee)
        .filter(ReservationAttendee.reservation_id == reservation_id)
        .all()
    )

    existing_map = {g.id: g for g in existing_guests}
    incoming_ids = [a.id for a in payload.attendees if a.id is not None]

    # 1) DELETE removed
    for g_id, guest in existing_map.items():
        if g_id not in incoming_ids:
            db.delete(guest)

    # 2) UPDATE or CREATE
    for a in payload.attendees:
        if a.id and a.id in existing_map:
            target = existing_map[a.id]
            for key, value in a.model_dump(exclude={"id", "reservation_id"}).items():
                setattr(target, key, value)
        else:
            db.add(
                ReservationAttendee(
                    **a.model_dump(exclude={"id"}),
                    reservation_id=reservation_id,
                    created_by_user_id=user.id,
                )
            )

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return toast_responses.error_server(f"Manifest sync failed: {str(e)}")

    return (
        db.query(ReservationAttendee)
        .filter(ReservationAttendee.reservation_id == reservation_id)
        .all()
    )


# ── DIRECTORY & LISTINGS ─────────────────────────────────────────────

@router.get("/users", response_model=List[UserPublic])
def ops_list_users(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "read")),
):
    """Staff directory view."""
    if scope != "all":
        return toast_responses.error_forbidden("User", "directory_access")

    return db.query(User).order_by(User.id.desc()).all()


@router.get("/attendees", response_model=List[ReservationAttendeeResponse])
def ops_list_all_attendees(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("ReservationAttendee", "read")),
):
    """Provides data for floor plan guest bubble population."""
    if scope != "all":
        return toast_responses.error_forbidden("ReservationAttendee", "read_all")

    return db.query(ReservationAttendee).all()
