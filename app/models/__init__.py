# app/models/__init__.py

from app.database import Base 

from .user import User
from .member import Member
from .dining_room import DiningRoom
from .table_entity import TableEntity  # Updated based on your error
from .reservation import Reservation
from .reservation_attendee import ReservationAttendee
from .menu_item import MenuItem
from .order import Order
from .order_item import OrderItem
from .activity_log import ActivityLog
from .audit_trail import AuditTrail
from .rule import Rule
from .fee import Fee
from .reservation_total import ReservationTotal
from .reservation_message import ReservationMessage
from .notification import Notification
from .daily_stat import DailyStat
from .seat import Seat
from .system_setting import SystemSetting

__all__ = [
    "Base",
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
    "SystemSetting",
]