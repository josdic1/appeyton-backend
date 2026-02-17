from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemResponse
from app.models.user import User
# Updated Imports
from app.utils.permissions import get_current_user, get_permission
from app.utils.query_helpers import apply_permission_filter

router = APIRouter()

@router.get("", response_model=list[MenuItemResponse])
def list_menu_items(
    category: str | None = Query(None),
    available_only: bool = Query(False),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("MenuItem", "read")),
):
    query = db.query(MenuItem)
    if category:
        query = query.filter(MenuItem.category == category)
    if available_only:
        query = query.filter(MenuItem.is_available == True)
        
    filtered_query = apply_permission_filter(query, MenuItem, scope, user.id)
    return filtered_query.order_by(MenuItem.category, MenuItem.display_order, MenuItem.name).all()

@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("MenuItem", "read")),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item