from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.utils.auth import get_current_user

ROLE_ORDER = {"member": 1, "staff": 2, "admin": 3}

def require_min_role(min_role: str):
    def _dep(current_user: User = Depends(get_current_user)) -> User:
        if ROLE_ORDER.get(current_user.role, 0) < ROLE_ORDER.get(min_role, 999):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return _dep
