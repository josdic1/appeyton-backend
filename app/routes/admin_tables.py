# app/routes/admin_tables.py
from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.table_entity import TableEntity
from app.models.seat import Seat
from app.models.reservation import Reservation
from app.schemas.table_entity import TableEntityCreate, TableEntityUpdate, TableEntityResponse
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission
from app.utils import toast_responses

router = APIRouter(tags=["Admin - Tables"])

POSITIONS = ["top", "right", "bottom", "left", "top-right", "bottom-right", "bottom-left", "top-left"]

@router.get("", response_model=List[TableEntityResponse])
def list_tables(
    db: Session = Depends(get_db),
    scope: str = Depends(get_permission("Table", "read")),
):
    """Admin view of all tables across all dining rooms."""
    if scope == "none":
        return toast_responses.error_forbidden("Table", "read")
        
    return (
        db.query(TableEntity)
        .order_by(TableEntity.dining_room_id.asc(), TableEntity.table_number.asc())
        .all()
    )


@router.post("", response_model=TableEntityResponse, status_code=status.HTTP_201_CREATED)
def create_table(
    payload: TableEntityCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Table", "write")),
):
    """Creates a table and automatically generates the associated seats."""
    if scope != "all":
        return toast_responses.error_forbidden("Table", "write")

    t = TableEntity(
        **payload.model_dump(),
        created_by_user_id=user.id,
        updated_by_user_id=user.id,
    )
    db.add(t)

    try:
        db.flush()  # get t.id

        for i in range(payload.seat_count):
            db.add(Seat(
                table_id=t.id,
                seat_number=i + 1,
                position=POSITIONS[i % len(POSITIONS)],
                is_accessible=False,
                is_available=True,
                created_by_user_id=user.id,
                updated_by_user_id=user.id,
            ))

        db.commit()
    except IntegrityError:
        db.rollback()
        return toast_responses.error_server("Conflict: Table number already exists in this room.")

    db.refresh(t)
    return t


@router.patch("/{table_id}", response_model=TableEntityResponse)
def update_table(
    table_id: int,
    payload: TableEntityUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Table", "write")),
):
    """Updates table metadata and syncs seat records if seat_count changed."""
    if scope != "all":
        return toast_responses.error_forbidden("Table", "write")

    t = db.query(TableEntity).filter(TableEntity.id == table_id).first()
    if not t:
        return toast_responses.error_not_found("Table", table_id)

    old_seat_count = t.seat_count
    updates = payload.model_dump(exclude_unset=True)

    for k, v in updates.items():
        setattr(t, k, v)

    t.updated_by_user_id = user.id
    new_seat_count = updates.get("seat_count")

    # Handle Seat Re-sync logic
    if new_seat_count is not None and new_seat_count != old_seat_count:
        existing_seats = db.query(Seat).filter(Seat.table_id == table_id).order_by(Seat.seat_number).all()
        current_count = len(existing_seats)

        if new_seat_count > current_count:
            for i in range(current_count, new_seat_count):
                db.add(Seat(
                    table_id=table_id,
                    seat_number=i + 1,
                    position=POSITIONS[i % len(POSITIONS)],
                    created_by_user_id=user.id,
                    updated_by_user_id=user.id,
                ))
        elif new_seat_count < current_count:
            seats_to_remove = existing_seats[new_seat_count:]
            for seat in seats_to_remove:
                db.delete(seat)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return toast_responses.error_server("Update failed: Table number conflict.")

    db.refresh(t)
    return t


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(
    table_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Table", "delete")),
):
    """Deletes a table if it has no active reservations."""
    if scope != "all":
        return toast_responses.error_forbidden("Table", "delete")

    t = db.query(TableEntity).filter(TableEntity.id == table_id).first()
    if not t:
        return toast_responses.error_not_found("Table", table_id)

    # Integrity Check
    has_res = db.query(Reservation.id).filter(Reservation.table_id == table_id).first()
    if has_res:
        return toast_responses.error_server("Cannot delete table: It has active reservations.")

    db.delete(t)
    db.commit()
    return None