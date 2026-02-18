from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database import get_db
from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemResponse
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission

router = APIRouter()

@router.get("/grouped", response_model=Dict[str, List[MenuItemResponse]])
def get_grouped_menu(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("MenuItem", "read")),
):
    """Categorizes menu items for the OrderManager UI."""
    items = db.query(MenuItem).filter(MenuItem.is_available == True).order_by(
        MenuItem.category, MenuItem.display_order
    ).all()
    
    grouped = {}
    for item in items:
        cat = item.category.capitalize()
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(item)
    return grouped

@router.get("", response_model=list[MenuItemResponse])
def list_menu_items(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("MenuItem", "read")),
):
    """General list for the static Digital Menu."""
    return db.query(MenuItem).all()