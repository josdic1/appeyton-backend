import json
import os
# ADD Session HERE:
from sqlalchemy.orm import Session 
from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.utils.auth import get_current_user
from app.models.activity_log import ActivityLog

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "permissions.json")

def load_acl():
    """Reads the live permissions from the JSON file."""
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"member": {}, "staff": {}, "admin": {}}

# FIX: Added Session import and made ip type hint optional
def save_acl(db: Session, user_id: int, new_acl: dict, ip: str | None = None):
    # 1. Load the old values
    old_acl = load_acl()
    
    # 2. Write the new file to disk
    with open(CONFIG_PATH, "w") as f:
        json.dump(new_acl, f, indent=2)

    # 3. Create a record in ActivityLog
    log = ActivityLog(
        user_id=user_id,
        action="update_permissions",
        resource_type="system_settings",
        details={
            "description": "Permission matrix updated via Admin Dashboard",
            "old_snapshot": old_acl,
            "new_snapshot": new_acl
        },
        ip_address=ip
    )
    db.add(log)
    db.commit()

def get_permission(entity: str, action: str):
    def dependency(user: User = Depends(get_current_user)):
        # Keep the Admin bypass for safety while testing
        if user.role == "admin":
            return "all"
        
        acl = load_acl()
        # Look for the role, then the entity (e.g., "DiningRoom")
        role_policy = acl.get(user.role, {}).get(entity, {})
        scope = role_policy.get(action, "none")
        
        if scope == "none":
            # This is exactly the error you see in your console
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Access Denied: {entity}:{action}"
            )
        return scope
    return dependency

