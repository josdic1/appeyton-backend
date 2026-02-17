from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dining_room import DiningRoom
from app.schemas.dining_room import DiningRoomCreate, DiningRoomUpdate, DiningRoomResponse
from app.models.user import User

from app.utils.permissions import get_current_user, get_permission
from app.utils.query_helpers import apply_permission_filter

router = APIRouter()

@router.post("", response_model=DiningRoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: DiningRoomCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("DiningRoom", "write")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Insufficient scope")

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
        raise HTTPException(status_code=409, detail="Dining room name already exists")

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
    if scope != "all":
        raise HTTPException(status_code=403, detail="Insufficient scope")

    room = db.query(DiningRoom).filter(DiningRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Dining room not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(room, k, v)

    room.updated_by_user_id = user.id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Dining room name already exists")

    db.refresh(room)
    return room

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("DiningRoom", "delete")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Insufficient scope")

    room = db.query(DiningRoom).filter(DiningRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Dining room not found")

    db.delete(room)
    db.commit()
    return None