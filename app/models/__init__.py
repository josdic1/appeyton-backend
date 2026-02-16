# app/models/__init__.py - COMPLETE VERSION

from app.models.user import User
from app.models.member import Member
from app.models.dining_room import DiningRoom
from app.models.table_entity import TableEntity
from app.models.reservation import Reservation
from app.models.reservation_attendee import ReservationAttendee
from app.models.menu_item import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem

# New models
from app.models.activity_log import ActivityLog
from app.models.audit_trail import AuditTrail
from app.models.rule import Rule
from app.models.fee import Fee
from app.models.reservation_total import ReservationTotal
from app.models.reservation_message import ReservationMessage
from app.models.notification import Notification
from app.models.daily_stat import DailyStat
from app.models.seat import Seat

__all__ = [
    "User",
    "Member",
    "DiningRoom",
    "TableEntity",
    "Reservation",
    "ReservationAttendee",
    "MenuItem",
    "Order",
    "OrderItem",
    "ActivityLog",
    "AuditTrail",
    "Rule",
    "Fee",
    "ReservationTotal",
    "ReservationMessage",
    "Notification",
    "DailyStat",
    "Seat",
]