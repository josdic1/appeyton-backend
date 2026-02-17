from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
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
from app.models.user import User
from app.utils.permissions import get_current_user, get_permission

router = APIRouter()


@router.post("", response_model=OrderWithItemsResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "write")),
):
    reservation = db.query(Reservation).filter(Reservation.id == payload.reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if scope == "own" and reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your reservation")

    # Create the order
    order = Order(reservation_id=reservation.id, status="incomplete", notes=payload.notes)
    db.add(order)
    db.flush()  # flush so order.id is available for OrderItem FKs

    # Create all items from payload
    for item_in in payload.items:
        # Verify the menu item exists and is available
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_in.menu_item_id).first()
        if not menu_item:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Menu item {item_in.menu_item_id} not found")
        if not menu_item.is_available:
            db.rollback()
            raise HTTPException(status_code=409, detail=f"{menu_item.name} is not available")

        # Verify the attendee belongs to this reservation
        attendee = db.query(ReservationAttendee).filter(
            ReservationAttendee.id == item_in.reservation_attendee_id,
            ReservationAttendee.reservation_id == reservation.id,
        ).first()
        if not attendee:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Attendee {item_in.reservation_attendee_id} not found on this reservation"
            )

        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=item_in.menu_item_id,
            reservation_attendee_id=item_in.reservation_attendee_id,
            quantity=item_in.quantity,
            unit_price=menu_item.price,  # snapshot the price at time of order
            special_instructions=item_in.special_instructions,
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)
    return order


@router.get("/{order_id}", response_model=OrderWithItemsResponse)
def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "read")),
):
    order = (
        db.query(Order)
        .options(joinedload(Order.items), joinedload(Order.reservation))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Safe ownership check — reservation is guaranteed loaded via joinedload
    if scope == "own" and order.reservation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your order")

    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    scope: str = Depends(get_permission("Order", "delete")),
):
    # Fetch first — 404 is more accurate than 403 for a non-existent record
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if scope != "all":
        raise HTTPException(status_code=403, detail="Only admins can delete full orders")

    db.delete(order)
    db.commit()
    return None