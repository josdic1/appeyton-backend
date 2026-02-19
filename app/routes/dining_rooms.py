# app/routes/dining_rooms.py
from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.dining_room import DiningRoom
from app.models.table_entity import TableEntity
from app.schemas.dining_room import DiningRoomCreate, DiningRoomUpdate, DiningRoomResponse
from app.schemas.table_entity import TableEntityResponse
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission
from app.utils import toast_responses

# IMPORTANT:
# main.py mounts this router at /api/dining-rooms
# so DO NOT add prefix="/dining-rooms" here.
router = APIRouter(tags=["Dining Rooms"])


# ── READ OPERATIONS ──────────────────────────────────────────────────

@router.get("", response_model=List[DiningRoomResponse])
def list_rooms(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("DiningRoom", "read")),
):
    """List all dining rooms."""
    if scope == "none":
        return toast_responses.error_forbidden("DiningRoom", "read")

    query = db.query(DiningRoom).options(joinedload(DiningRoom.tables))
    if active_only:
        query = query.filter(DiningRoom.is_active == True)

    return query.order_by(DiningRoom.display_order).all()


@router.get("/{room_id}", response_model=DiningRoomResponse)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("DiningRoom", "read")),
):
    """Fetch a single room layout."""
    if scope == "none":
        return toast_responses.error_forbidden("DiningRoom", "read")

    room = (
        db.query(DiningRoom)
        .options(joinedload(DiningRoom.tables))
        .filter(DiningRoom.id == room_id)
        .first()
    )
    if not room:
        return toast_responses.error_not_found("Dining Room", room_id)
    return room


# ── WRITE OPERATIONS (Admin/Staff Only) ──────────────────────────────

@router.post("", response_model=DiningRoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: DiningRoomCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("DiningRoom", "write")),
):
    """Admin only: Create a new dining room section."""
    if scope != "all":
        return toast_responses.error_forbidden("DiningRoom", "write")

    room = DiningRoom(
        name=payload.name,
        is_active=payload.is_active,
        display_order=payload.display_order,
        meta=payload.meta,
        created_by_user_id=user.id,
        updated_by_user_id=user.id,
    )
    db.add(room)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return toast_responses.error_server("Dining room name already exists.")

    db.refresh(room)
    return room


@router.patch("/{room_id}", response_model=DiningRoomResponse)
def update_room(
    room_id: int,
    payload: DiningRoomUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("DiningRoom", "write")),
):
    """Admin only: Update room metadata or status."""
    if scope != "all":
        return toast_responses.error_forbidden("DiningRoom", "write")

    room = db.query(DiningRoom).filter(DiningRoom.id == room_id).first()
    if not room:
        return toast_responses.error_not_found("Dining Room", room_id)

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(room, k, v)

    room.updated_by_user_id = user.id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return toast_responses.error_server("Update failed: Room name conflict detected.")

    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("DiningRoom", "delete")),
):
    """Admin only: Remove a room."""
    if scope != "all":
        return toast_responses.error_forbidden("DiningRoom", "delete")

    room = db.query(DiningRoom).filter(DiningRoom.id == room_id).first()
    if not room:
        return toast_responses.error_not_found("Dining Room", room_id)

    db.delete(room)
    db.commit()
    return None


# ── TABLES ───────────────────────────────────────────────────────────

@router.get("/{room_id}/tables", response_model=List[TableEntityResponse])
def get_room_tables(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("DiningRoom", "read")),
):
    """Fetch raw table list for a specific room layout."""
    if scope == "none":
        return toast_responses.error_forbidden("DiningRoom", "read")

    tables = (
        db.query(TableEntity)
        .filter(TableEntity.dining_room_id == room_id)
        .order_by(TableEntity.table_number)
        .all()
    )
    return tables
