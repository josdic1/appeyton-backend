# app/routes/dining_rooms.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.dining_room import DiningRoom
from app.models.table_entity import TableEntity
from app.schemas.dining_room import DiningRoomResponse
from app.schemas.table_entity import TableEntityResponse
from app.utils.permissions import require_min_role
from app.models.user import User

router = APIRouter()


@router.get("", response_model=list[DiningRoomResponse])
def list_rooms(
    db: Session = Depends(get_db),
    _user: User = Depends(require_min_role("member")),
):
    """List all active dining rooms with computed capacity"""
    return (
        db.query(DiningRoom)
        .options(joinedload(DiningRoom.tables))
        .filter(DiningRoom.is_active == True)
        .order_by(DiningRoom.display_order)
        .all()
    )


@router.get("/tables/all", response_model=list[TableEntityResponse])
def list_all_tables(
    db: Session = Depends(get_db),
    _user: User = Depends(require_min_role("member")),
):
    """List all tables across all rooms (for members creating reservations)"""
    return (
        db.query(TableEntity)
        .order_by(TableEntity.dining_room_id, TableEntity.table_number)
        .all()
    )


@router.get("/{room_id}", response_model=DiningRoomResponse)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_min_role("member")),
):
    """Get a single dining room with computed capacity"""
    room = (
        db.query(DiningRoom)
        .options(joinedload(DiningRoom.tables))
        .filter(DiningRoom.id == room_id)
        .first()
    )
    if not room:
        raise HTTPException(status_code=404, detail="Dining room not found")
    return room


@router.get("/{room_id}/tables", response_model=list[TableEntityResponse])
def list_room_tables(
    room_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_min_role("member")),
):
    """List all tables in a specific dining room"""
    return (
        db.query(TableEntity)
        .filter(TableEntity.dining_room_id == room_id)
        .order_by(TableEntity.table_number)
        .all()
    )