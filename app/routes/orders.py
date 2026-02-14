# app/routes/orders.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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
    OrderItemResponse,
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
    """
    Create an order for a reservation.
    
    - Members: Can only order for their own reservations
    - Staff/Admin: Can order for any reservation
    """
    # Get the reservation
    reservation = db.query(Reservation).filter(Reservation.id == payload.reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    assert reservation is not None

    # Authorization check: Members can only order for their own reservations
    if user.role == "member":
        if reservation.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only order for your own reservations"
            )
    
    # Staff/Admin can order for any reservation (no additional check needed)

    # Check if order already exists for this reservation
    existing_order = db.query(Order).filter(Order.reservation_id == reservation.id).first()
    if existing_order:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order already exists for this reservation. Use PATCH to add items."
        )

    # Create the order
    order = Order(
        reservation_id=reservation.id,
        status="incomplete",
        notes=payload.notes,
    )
    db.add(order)
    db.flush()  # Get order.id

    # Add order items
    order_items = []
    for item_data in payload.items:
        # Verify menu item exists
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {item_data.menu_item_id} not found")
        
        if not menu_item.is_available:
            raise HTTPException(status_code=409, detail=f"{menu_item.name} is not available")

        # Verify attendee belongs to this reservation
        attendee = db.query(ReservationAttendee).filter(
            ReservationAttendee.id == item_data.reservation_attendee_id,
            ReservationAttendee.reservation_id == reservation.id,
        ).first()
        if not attendee:
            raise HTTPException(
                status_code=404,
                detail=f"Attendee {item_data.reservation_attendee_id} not found in this reservation"
            )

        # Create order item with price snapshot
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            reservation_attendee_id=attendee.id,
            quantity=item_data.quantity,
            unit_price=menu_item.price,  # Snapshot current price
            special_instructions=item_data.special_instructions,
        )
        db.add(order_item)
        order_items.append(order_item)

    db.commit()
    db.refresh(order)

    # Return order with items
    return {
        "id": order.id,
        "reservation_id": order.reservation_id,
        "status": order.status,
        "notes": order.notes,
        "items": [
            {
                "id": item.id,
                "order_id": item.order_id,
                "reservation_attendee_id": item.reservation_attendee_id,
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "special_instructions": item.special_instructions,
                "meta": item.meta,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            for item in order_items
        ],
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


@router.get("/{order_id}", response_model=OrderWithItemsResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """
    Get an order with all items.
    
    - Members: Can only view their own reservation's orders
    - Staff/Admin: Can view any order
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Get reservation to check ownership
    reservation = db.query(Reservation).filter(Reservation.id == order.reservation_id).first()
    
    assert reservation is not None

    # Authorization check
    if user.role == "member":
        if reservation.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your order")

    # Get order items
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

    return {
        "id": order.id,
        "reservation_id": order.reservation_id,
        "status": order.status,
        "notes": order.notes,
        "items": [
            {
                "id": item.id,
                "order_id": item.order_id,
                "reservation_attendee_id": item.reservation_attendee_id,
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "special_instructions": item.special_instructions,
                "meta": item.meta,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
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
    """
    Update order status/notes (staff/admin only).
    
    Use this to mark orders as 'complete', 'cancelled', etc.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(order, k, v)

    db.commit()
    db.refresh(order)
    return order


@router.get("/reservation/{reservation_id}", response_model=OrderWithItemsResponse)
def get_order_by_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role("member")),
):
    """
    Get the order for a specific reservation.
    
    - Members: Can only view their own reservation's order
    - Staff/Admin: Can view any reservation's order
    """
    # Get reservation to check ownership
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    assert reservation is not None

    # Authorization check
    if user.role == "member":
        if reservation.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your reservation")

    # Get order
    order = db.query(Order).filter(Order.reservation_id == reservation_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="No order found for this reservation")

    # Get order items
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

    return {
        "id": order.id,
        "reservation_id": order.reservation_id,
        "status": order.status,
        "notes": order.notes,
        "items": [
            {
                "id": item.id,
                "order_id": item.order_id,
                "reservation_attendee_id": item.reservation_attendee_id,
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "special_instructions": item.special_instructions,
                "meta": item.meta,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            for item in items
        ],
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }