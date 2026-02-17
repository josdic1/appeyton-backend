# app/routes/order_items.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.order import OrderItemUpdate, OrderItemResponse
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission

router = APIRouter()

@router.patch("/{item_id}", response_model=OrderItemResponse)
def update_order_item(
    item_id: int,
    payload: OrderItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "write")),
):
    # joinedload ensures item.order and order.reservation are available
    item = (
        db.query(OrderItem)
        .options(joinedload(OrderItem.order).joinedload(Order.reservation))
        .filter(OrderItem.id == item_id)
        .first()
    )
    
    if not item: 
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Ownership guard based on Matrix Scope
    if scope == "own":
        if not item.order or not item.order.reservation or item.order.reservation.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not your order item")
    
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "delete")),
):
    item = (
        db.query(OrderItem)
        .options(joinedload(OrderItem.order).joinedload(Order.reservation))
        .filter(OrderItem.id == item_id)
        .first()
    )
    
    if not item: 
        raise HTTPException(status_code=404, detail="Item not found")
    
    if scope == "own":
        if not item.order or not item.order.reservation or item.order.reservation.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not your order item")
    
    db.delete(item)
    db.commit()
    return None