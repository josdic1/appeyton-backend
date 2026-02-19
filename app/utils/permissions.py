# app/utils/permissions.py
from __future__ import annotations
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from typing import Dict, Any, Literal

from app.models.user import User
from app.models.system_setting import SystemSetting
from app.models.activity_log import ActivityLog
from app.utils.auth import get_current_user
from app.database import get_db

ACL_KEY = "permissions_matrix"

# Initialize with the default so it is NEVER None
_ACL_CACHE: Dict[str, Any] = {}

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

def load_acl(db: Session, force_refresh: bool = False) -> Dict[str, Any]:
    """Retrieves the ACL. Logic ensures a Dict is always returned."""
    global _ACL_CACHE
    
    # If cache is populated and we aren't forcing, return it
    if _ACL_CACHE and not force_refresh:
        return _ACL_CACHE

    setting = db.query(SystemSetting).filter(SystemSetting.key == ACL_KEY).first()
    
    # Prove to Pylance that result is a Dict
    result: Dict[str, Any] = DEFAULT_ACL
    if setting and isinstance(setting.value, dict):
        result = setting.value
        
    _ACL_CACHE = result
    return result

def save_acl(db: Session, user_id: int, new_acl: Dict[str, Any], ip: str | None = None) -> None:
    setting = db.query(SystemSetting).filter(SystemSetting.key == ACL_KEY).first()
    old_acl = setting.value if setting else None

    if not setting:
        setting = SystemSetting(key=ACL_KEY)
        db.add(setting)

    setting.value = new_acl
    setting.updated_by_user_id = user_id
    db.flush() 

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
    
    # Invalidate cache
    load_acl(db, force_refresh=True)

def get_permission(entity: str, action: str):
    def dependency(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Literal["all", "own"]:
        if user.role == "admin":
            return "all"

        acl = load_acl(db)
        role_policy: Dict[str, Any] = acl.get(user.role, {})
        entity_policy: Dict[str, Any] = role_policy.get(entity, {})
        scope = entity_policy.get(action, "none")

        if scope == "none":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {entity}:{action}",
            )
        
        return scope # type: ignore

    return dependency