# app/utils/toast_responses.py
from datetime import datetime, date, time as time_type
from typing import List, Optional, Any
from app.schemas.toast import ToastResponse, ActionButton

def success_booking(
    table_number: int,
    party_size: int,
    user_name: str,
    booking_date: date,
    start_time: time_type,
    meal_type: str,
    dining_room_name: str,
    reservation_id: int,
    elapsed_ms: int
) -> ToastResponse:
    """Successful reservation booking"""
    return ToastResponse(
        status="success",
        what=f"Table {table_number} booked for {party_size} people",
        who=f"Reserved under your name: {user_name}",
        when=f"{booking_date.strftime('%a %b %d')}, {start_time.strftime('%I:%M%p')} {meal_type}",
        why="All validation passed, confirmation email sent",
        where=f"{dining_room_name}, {meal_type} service confirmed",
        how="Add to calendar or view full details",
        actions=[
            ActionButton(label="Add to Calendar", action="calendar", params={"reservation_id": reservation_id}),
            ActionButton(label="View Reservation", action="navigate", params={"view": f"/reservations/{reservation_id}"}),
            ActionButton(label="Add Attendees", action="navigate", params={"view": f"/reservations/{reservation_id}/attendees"}),
        ],
        meta={"response_time_ms": elapsed_ms, "reservation_id": reservation_id}
    )

def error_table_taken(
    table_num: int,
    booking_date: date,
    meal_type: str,
    alternatives: List[Any]
) -> ToastResponse:
    """Table already booked - offer alternatives"""
    alt_actions = [
        ActionButton(
            label=f"Try Table {tbl_num}", 
            action="retry", 
            params={"table_id": tbl_id}
        )
        for tbl_id, tbl_num in alternatives[:2]
    ]
    
    return ToastResponse(
        status="error",
        what=f"Table {table_num} already booked for that time",
        who="Another member reserved it seconds ago",
        when=f"{booking_date.strftime('%a %b %d')}, {meal_type} slot taken",
        why="Two people clicked Book at same time",
        where="This specific table is now fully booked",
        how="Try different time or pick nearby table",
        actions=alt_actions + [
            ActionButton(label="See All Available", action="navigate", params={"view": "/availability"})
        ],
        meta={"alternatives_count": len(alternatives)}
    )

def error_not_found(resource: str, resource_id: Optional[int] = None) -> ToastResponse:
    """Resource not found in database"""
    return ToastResponse(
        status="error",
        what=f"{resource} not found in system",
        who="May have been deleted by admin recently",
        when="Checked database just now at request",
        why="Data changed since you loaded this page",
        where="Database shows no matching record ID found",
        how="Refresh page to see current valid options",
        actions=[
            ActionButton(label="Refresh Page", action="reload"),
            ActionButton(label="Go Home", action="navigate", params={"view": "/"}),
        ],
        meta={"resource_id": resource_id} if resource_id else None
    )

def error_unauthorized(required_role: str) -> ToastResponse:
    """User lacks permission"""
    return ToastResponse(
        status="error",
        what="You don't have permission for this action",
        who=f"Only {required_role} users allowed here now",
        when="Access level checked when request was made",
        why="Your account role doesn't allow this operation",
        where="This section requires higher permission level exactly",
        how="Contact admin to request access role upgrade",
        actions=[
            ActionButton(label="Go Home", action="navigate", params={"view": "/"}),
        ]
    )

def error_validation(field: str, issue: str, suggestion: str) -> ToastResponse:
    """Validation error"""
    return ToastResponse(
        status="error",
        what=f"Invalid {field}: {issue}",
        who="Your input didn't pass validation rules here",
        when="Checked when you submitted the form request",
        why=f"{field} {issue}",
        where=f"Form validation failed on {field} field exactly",
        how=suggestion,
        actions=[
            ActionButton(label="Try Again", action="dismiss"),
        ]
    )

def success_generic(action: str, details: str, elapsed_ms: int) -> ToastResponse:
    """Generic success message"""
    return ToastResponse(
        status="success",
        what=f"{action} completed successfully",
        who="You performed this action just now successfully",
        when="Completed just now at this exact moment",
        why="All validation passed, operation completed successfully",
        where=details,
        how="No further action needed from you now",
        actions=[
            ActionButton(label="Done", action="dismiss"),
        ],
        meta={"response_time_ms": elapsed_ms}
    )

def error_server(error_msg: Optional[str] = None) -> ToastResponse:
    """Unexpected server error"""
    return ToastResponse(
        status="error",
        what="Server error occurred during request processing",
        who="Not your fault, this is bug code",
        when="Just happened when processing your last request",
        why="Unexpected condition server couldn't handle at all",
        where="Backend server encountered unhandled exception error here",
        how="Try again shortly or report if persists",
        actions=[
            ActionButton(label="Try Again", action="retry"),
            ActionButton(label="Report Bug", action="navigate", params={"view": "/support"}),
        ],
        meta={"error": error_msg} if error_msg else None
    )

def success_order_created(
    order_id: int,
    item_count: int,
    reservation_id: int,
    elapsed_ms: int
) -> ToastResponse:
    """Order successfully created"""
    return ToastResponse(
        status="success",
        what=f"Order created with {item_count} items successfully",
        who="Your order has been sent to kitchen",
        when="Order placed just now for this meal",
        why="All items available, kitchen has been notified",
        where=f"Linked to reservation ID {reservation_id} permanently",
        how="Kitchen preparing, track status in reservations page",
        actions=[
            ActionButton(label="View Order", action="navigate", params={"view": f"/orders/{order_id}"}),
            ActionButton(label="Add More Items", action="navigate", params={"view": f"/orders/{order_id}/edit"}),
        ],
        meta={"response_time_ms": elapsed_ms, "order_id": order_id, "item_count": item_count}
    )

def error_menu_item_unavailable(item_name: str) -> ToastResponse:
    """Menu item not available"""
    return ToastResponse(
        status="error",
        what=f"{item_name} is not available right now",
        who="Kitchen marked this item as unavailable today",
        when="Status checked just now when processing order",
        why="Item out of stock or not served",
        where="This specific menu item cannot be ordered",
        how="Choose different item from available menu options",
        actions=[
            ActionButton(label="View Menu", action="navigate", params={"view": "/menu"}),
        ]
    )