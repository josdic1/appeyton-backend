# app/routes/orders.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.reservation import Reservation
from app.models.menu_item import MenuItem
from app.models.reservation_attendee import ReservationAttendee
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderWithItemsResponse,
)
from app.utils.permissions import require_min_role
from app.models.user import User

router = APIRouter()


@router.post("", response_model=OrderWithItemsResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    reservation = db.query(Reservation).filter(Reservation.id == payload.reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if user.role == "member" and reservation.user_id != user.id:
        raise HTTPException(403, "Not your reservation")

    existing = db.query(Order).filter(Order.reservation_id == reservation.id).first()
    if existing:
        raise HTTPException(409, "Order already exists for this reservation")

    order = Order(
        reservation_id=reservation.id,
        status="incomplete",
        notes=payload.notes,
    )
    db.add(order)
    db.flush()

    order_items = []
    for item_data in payload.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
        if not menu_item or not menu_item.is_available:
            raise HTTPException(404, f"Menu item {item_data.menu_item_id} not available")

        attendee = db.query(ReservationAttendee).filter(
            ReservationAttendee.id == item_data.reservation_attendee_id,
            ReservationAttendee.reservation_id == reservation.id
        ).first()
        if not attendee:
            raise HTTPException(404, f"Attendee {item_data.reservation_attendee_id} not found")

        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            reservation_attendee_id=attendee.id,
            quantity=item_data.quantity,
            unit_price=menu_item.price,
            special_instructions=item_data.special_instructions,
        )
        db.add(order_item)
        order_items.append(order_item)

    db.commit()
    db.refresh(order)

    return {
        "id": order.id,
        "reservation_id": order.reservation_id,
        "status": order.status,
        "notes": order.notes,
        "items": [
            {
                "id": i.id,
                "order_id": i.order_id,
                "reservation_attendee_id": i.reservation_attendee_id,
                "menu_item_id": i.menu_item_id,
                "quantity": i.quantity,
                "unit_price": i.unit_price,
                "special_instructions": i.special_instructions,
                "meta": i.meta,
                "created_at": i.created_at,
                "updated_at": i.updated_at,
                "menu_item_name": db.query(MenuItem.name).filter(MenuItem.id == i.menu_item_id).scalar(),
                "attendee_name": db.query(ReservationAttendee.name).filter(ReservationAttendee.id == i.reservation_attendee_id).scalar(),
            }
            for i in order_items
        ],
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


# FIXED: Split into two separate routes instead of dual decorator
@router.get("/{order_id}", response_model=OrderWithItemsResponse)
def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """Get order by order ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    
    reservation = db.query(Reservation).filter(Reservation.id == order.reservation_id).first()
    if not reservation:
        raise HTTPException(404, "Reservation not found")
    if user.role == "member" and reservation.user_id != user.id:
        raise HTTPException(403, "Not your reservation")

    items = (
        db.execute(
            select(
                OrderItem,
                MenuItem.name.label("menu_item_name"),
                ReservationAttendee.name.label("attendee_name")
            )
            .join(MenuItem, OrderItem.menu_item_id == MenuItem.id)
            .join(ReservationAttendee, OrderItem.reservation_attendee_id == ReservationAttendee.id)
            .where(OrderItem.order_id == order.id)
        )
        .all()
    )

    return {
        "id": order.id,
        "reservation_id": order.reservation_id,
        "status": order.status,
        "notes": order.notes,
        "items": [
            {
                "id": item.OrderItem.id,
                "order_id": item.OrderItem.order_id,
                "reservation_attendee_id": item.OrderItem.reservation_attendee_id,
                "menu_item_id": item.OrderItem.menu_item_id,
                "quantity": item.OrderItem.quantity,
                "unit_price": item.OrderItem.unit_price,
                "special_instructions": item.OrderItem.special_instructions,
                "meta": item.OrderItem.meta,
                "created_at": item.OrderItem.created_at,
                "updated_at": item.OrderItem.updated_at,
                "menu_item_name": item.menu_item_name,
                "attendee_name": item.attendee_name,
            }
            for item in items
        ],
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


@router.get("/reservation/{reservation_id}", response_model=OrderWithItemsResponse)
def get_order_by_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """Get order by reservation ID"""
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(404, "Reservation not found")
    
    if user.role == "member" and reservation.user_id != user.id:
        raise HTTPException(403, "Not your reservation")
    
    order = db.query(Order).filter(Order.reservation_id == reservation_id).first()
    if not order:
        raise HTTPException(404, "No order found for this reservation")

    items = (
        db.execute(
            select(
                OrderItem,
                MenuItem.name.label("menu_item_name"),
                ReservationAttendee.name.label("attendee_name")
            )
            .join(MenuItem, OrderItem.menu_item_id == MenuItem.id)
            .join(ReservationAttendee, OrderItem.reservation_attendee_id == ReservationAttendee.id)
            .where(OrderItem.order_id == order.id)
        )
        .all()
    )

    return {
        "id": order.id,
        "reservation_id": order.reservation_id,
        "status": order.status,
        "notes": order.notes,
        "items": [
            {
                "id": item.OrderItem.id,
                "order_id": item.OrderItem.order_id,
                "reservation_attendee_id": item.OrderItem.reservation_attendee_id,
                "menu_item_id": item.OrderItem.menu_item_id,
                "quantity": item.OrderItem.quantity,
                "unit_price": item.OrderItem.unit_price,
                "special_instructions": item.OrderItem.special_instructions,
                "meta": item.OrderItem.meta,
                "created_at": item.OrderItem.created_at,
                "updated_at": item.OrderItem.updated_at,
                "menu_item_name": item.menu_item_name,
                "attendee_name": item.attendee_name,
            }
            for item in items
        ],
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("staff")),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(order, k, v)

    db.commit()
    db.refresh(order)
    return order


# NEW: DELETE endpoint to fix the 409 issue
@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("admin")),
):
    """Delete an order and all its items"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    
    # Delete order items first (cascade)
    db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
    
    # Delete the order
    db.delete(order)
    db.commit()
    
    return None