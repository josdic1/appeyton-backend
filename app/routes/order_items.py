# app/routes/order_items.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.reservation import Reservation
from app.models.menu_item import MenuItem
from app.models.reservation_attendee import ReservationAttendee
from app.schemas.order import OrderItemCreate, OrderItemUpdate, OrderItemResponse
from app.utils.permissions import require_min_role
from app.models.user import User

router = APIRouter()


@router.post("", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
def add_order_item(
    payload: OrderItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """Add item to existing order"""
    order = db.query(Order).filter(Order.id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    reservation = db.query(Reservation).filter(Reservation.id == order.reservation_id).first()
    
    if user.role == "member" and reservation and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    
    menu_item = db.query(MenuItem).filter(MenuItem.id == payload.menu_item_id).first()
    if not menu_item or not menu_item.is_available:
        raise HTTPException(status_code=404, detail="Menu item not available")
    
    attendee = db.query(ReservationAttendee).filter(
        ReservationAttendee.id == payload.reservation_attendee_id,
        ReservationAttendee.reservation_id == order.reservation_id
    ).first()
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    
    item = OrderItem(
        order_id=order.id,
        menu_item_id=menu_item.id,
        reservation_attendee_id=attendee.id,
        quantity=payload.quantity,
        unit_price=menu_item.price,
        special_instructions=payload.special_instructions
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=OrderItemResponse)
def update_order_item(
    item_id: int,
    payload: OrderItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """Update order item quantity or instructions"""
    item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    order = db.query(Order).filter(Order.id == item.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    reservation = db.query(Reservation).filter(Reservation.id == order.reservation_id).first()
    
    if user.role == "member" and reservation and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """Remove item from order"""
    item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    order = db.query(Order).filter(Order.id == item.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    reservation = db.query(Reservation).filter(Reservation.id == order.reservation_id).first()
    
    if user.role == "member" and reservation and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    
    db.delete(item)
    db.commit()
    return None