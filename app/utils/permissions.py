# app/utils/permissions.py
from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.utils.auth import get_current_user

ROLE_ORDER = {"member": 1, "staff": 2, "admin": 3}


def require_min_role(min_role: str):
    def dep(user: User = Depends(get_current_user)) -> User:
        if ROLE_ORDER.get(user.role, 0) < ROLE_ORDER.get(min_role, 999):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return dep


def require_exact_role(role: str):
    def dep(user: User = Depends(get_current_user)) -> User:
        if user.role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return dep


def require_any_role(*roles: str):
    allowed = set(roles)

    def dep(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return dep
