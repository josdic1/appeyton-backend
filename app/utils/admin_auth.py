# utils/admin_auth.py
from fastapi import HTTPException, status, Depends
from app.models.user import User
from app.utils.auth import get_current_user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
