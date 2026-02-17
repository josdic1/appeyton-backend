# app/utils/permissions.py
import json
import os
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.models.system_setting import SystemSetting
from app.models.activity_log import ActivityLog
from app.utils.auth import get_current_user
from app.database import get_db

# The key we use in system_settings table
ACL_KEY = "permissions_matrix"

# Fallback default — used only if no row exists in DB yet
DEFAULT_ACL = {
    "member": {
        "Reservation": {"read": "own", "write": "own", "delete": "own"},
        "ReservationAttendee": {"read": "own", "write": "own", "delete": "own"},
        "MenuItem": {"read": "all", "write": "none", "delete": "none"},
        "Order": {"read": "own", "write": "own", "delete": "none"},
        "OrderItem": {"read": "own", "write": "own", "delete": "none"},
        "User": {"read": "own", "write": "own", "delete": "none"},
        "Member": {"read": "own", "write": "own", "delete": "none"},
        "DiningRoom": {"read": "all", "write": "none", "delete": "none"},
        "Table": {"read": "all", "write": "none", "delete": "none"},
        "ReservationMessage": {"read": "own", "write": "own", "delete": "none"},
        "DailyStat": {"read": "none", "write": "none", "delete": "none"},
        "AuditTrail": {"read": "none", "write": "none", "delete": "none"},
        "Notification": {"read": "own", "write": "none", "delete": "own"},
    },
    "staff": {
        "Reservation": {"read": "all", "write": "all", "delete": "all"},
        "ReservationAttendee": {"read": "all", "write": "all", "delete": "all"},
        "MenuItem": {"read": "all", "write": "all", "delete": "none"},
        "Order": {"read": "all", "write": "all", "delete": "all"},
        "OrderItem": {"read": "all", "write": "all", "delete": "all"},
        "User": {"read": "all", "write": "none", "delete": "none"},
        "Member": {"read": "all", "write": "all", "delete": "none"},
        "DiningRoom": {"read": "all", "write": "all", "delete": "none"},
        "Table": {"read": "all", "write": "all", "delete": "none"},
        "ReservationMessage": {"read": "all", "write": "all", "delete": "none"},
        "DailyStat": {"read": "all", "write": "none", "delete": "none"},
        "AuditTrail": {"read": "none", "write": "none", "delete": "none"},
        "Notification": {"read": "all", "write": "all", "delete": "all"},
    },
    "admin": {
        "Reservation": {"read": "all", "write": "all", "delete": "all"},
        "ReservationAttendee": {"read": "all", "write": "all", "delete": "all"},
        "MenuItem": {"read": "all", "write": "all", "delete": "all"},
        "Order": {"read": "all", "write": "all", "delete": "all"},
        "OrderItem": {"read": "all", "write": "all", "delete": "all"},
        "User": {"read": "all", "write": "all", "delete": "all"},
        "Member": {"read": "all", "write": "all", "delete": "all"},
        "DiningRoom": {"read": "all", "write": "all", "delete": "all"},
        "Table": {"read": "all", "write": "all", "delete": "all"},
        "ReservationMessage": {"read": "all", "write": "all", "delete": "all"},
        "DailyStat": {"read": "all", "write": "all", "delete": "all"},
        "AuditTrail": {"read": "all", "write": "all", "delete": "all"},
        "Notification": {"read": "all", "write": "all", "delete": "all"},
    },
}


def load_acl(db: Session) -> dict:
    setting = db.query(SystemSetting).filter(SystemSetting.key == ACL_KEY).first()
    if setting and setting.value:
        return setting.value
    return DEFAULT_ACL


def save_acl(db: Session, user_id: int, new_acl: dict, ip: str | None = None) -> None:
    # Capture old value before overwriting
    setting = db.query(SystemSetting).filter(SystemSetting.key == ACL_KEY).first()
    old_acl = setting.value if setting else None

    if not setting:
        setting = SystemSetting(key=ACL_KEY)
        db.add(setting)

    setting.value = new_acl
    setting.updated_by_user_id = user_id
    db.flush()  # write the setting before logging

    log = ActivityLog(
        user_id=user_id,
        action="update_permissions",
        resource_type="system_settings",
        details={
            "description": "Permission matrix updated via Admin Dashboard",
            "old_snapshot": old_acl,
            "new_snapshot": new_acl,
        },
        ip_address=ip,
    )
    db.add(log)
    db.commit()


def get_permission(entity: str, action: str):
    """FastAPI dependency — checks the ACL and returns the scope.

    Returns: 'all' | 'own'
    Raises:  403 if scope is 'none'
    """
    def dependency(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        if user.role == "admin":
            return "all"

        acl = load_acl(db)
        role_policy: dict = acl.get(user.role) or {}
        entity_policy: dict = role_policy.get(entity) or {}
        scope = entity_policy.get(action, "none")

        if scope == "none":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: {entity}:{action}",
            )
        return scope

    return dependency