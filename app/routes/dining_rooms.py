from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.dining_room import DiningRoom
from app.models.table_entity import TableEntity
from app.schemas.dining_room import DiningRoomResponse
from app.schemas.table_entity import TableEntityResponse
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission

router = APIRouter()

@router.get("", response_model=list[DiningRoomResponse])
def list_rooms(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("DiningRoom", "read")),
):
    # Dining rooms are usually 'all' read for members to book
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
    room = db.query(DiningRoom).options(joinedload(DiningRoom.tables)).filter(DiningRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Dining room not found")
    return room