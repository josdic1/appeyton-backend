from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.table_entity import TableEntity
from app.schemas.table_entity import TableEntityCreate, TableEntityUpdate, TableEntityResponse
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission

router = APIRouter()

@router.get("", response_model=list[TableEntityResponse])
def list_tables(
    db: Session = Depends(get_db),
    scope: str = Depends(get_permission("Table", "read")),
):
    # Tables are generally 'all' read for admin views
    return db.query(TableEntity).order_by(TableEntity.dining_room_id.asc(), TableEntity.table_number.asc()).all()

@router.post("", response_model=TableEntityResponse, status_code=status.HTTP_201_CREATED)
def create_table(
    payload: TableEntityCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Table", "write")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin scope required")

    t = TableEntity(
        **payload.model_dump(),
        created_by_user_id=user.id,
        updated_by_user_id=user.id,
    )
    db.add(t)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Table number already exists in that dining room")

    db.refresh(t)
    return t

@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(
    table_id: int,
    db: Session = Depends(get_db),
    scope: str = Depends(get_permission("Table", "delete")),
):
    if scope != "all":
        raise HTTPException(status_code=403, detail="Admin scope required")

    t = db.query(TableEntity).filter(TableEntity.id == table_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Table not found")

    db.delete(t)
    db.commit()
    return None