# app/routes/menu_items.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemResponse
from app.utils.permissions import require_min_role
from app.models.user import User

router = APIRouter()


@router.get("", response_model=list[MenuItemResponse])
def list_menu_items(
    category: str | None = Query(None),
    available_only: bool = Query(False),
    db: Session = Depends(get_db),
    _user: User = Depends(require_min_role("member")),
):
    query = db.query(MenuItem)
    if category:
        query = query.filter(MenuItem.category == category)
    if available_only:
        query = query.filter(MenuItem.is_available == True)
    return query.order_by(MenuItem.category, MenuItem.display_order, MenuItem.name).all()


@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_min_role("member")),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item