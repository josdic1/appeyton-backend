from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.reservation import Reservation
from app.models.dining_room import DiningRoom
from app.models.table_entity import TableEntity
from app.utils.permissions import get_current_user, get_permission
from app.schemas.user_public import UserPublic
from app.schemas.reservation import ReservationResponse
from app.schemas.dining_room import DiningRoomResponse
from app.schemas.table_entity import TableEntityResponse

router = APIRouter()

@router.get("/users", response_model=list[UserPublic])
def ops_list_users(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("User", "read")),
):
    if scope != "all":
        raise HTTPException(403, "Staff access required")
    return db.query(User).order_by(User.id.desc()).all()

@router.get("/reservations", response_model=list[ReservationResponse])
def ops_list_reservations(
    date: str | None = Query(None, description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Reservation", "read")),
):
    if scope != "all":
        raise HTTPException(403, "Staff access required")
        
    q = db.query(Reservation)
    if date:
        q = q.filter(Reservation.date == date)
    return q.order_by(Reservation.start_time.asc()).all()

@router.get("/tables", response_model=list[TableEntityResponse])
def ops_list_tables(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Table", "read")),
):
    if scope != "all":
        raise HTTPException(403, "Staff access required")
    return db.query(TableEntity).all()