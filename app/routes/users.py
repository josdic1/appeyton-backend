from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, TokenResponse
from app.utils.auth import create_access_token, get_current_user, BLOCKED_STATUSES

# No prefix here; handled by app.include_router(users.router, prefix="/api/users") in main.py
router = APIRouter(tags=["Users"])

# ── Public: no auth required ──────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    try:
        # 1. Fetch the user
        user = db.query(User).filter(User.email == payload.email).first()

        # 2. Validate Credentials
        if not user or not user.check_password(payload.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. Check Account Status
        if user.membership_status in BLOCKED_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account {user.membership_status}. Contact an administrator.",
            )

        # 4. Update Persistence Logic
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        
        # CRITICAL FIX: Refresh the object after commit.
        # This keeps the attributes loaded so Pydantic can read them for TokenResponse.
        db.refresh(user)
        
        return {
            "access_token": create_access_token(user_id=user.id, role=user.role),
            "token_type": "bearer",
            "user": user,
        }
    except HTTPException:
        # Re-raise HTTP exceptions so they aren't caught by the general Exception block
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Login error: {e}")
        # Return the actual error string in dev to help debugging
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    user = User(
        email=user_in.email,
        name=user_in.name,
        role="member",
        membership_status="active",
        guest_allowance=4,
    )
    user.set_password(user_in.password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ── Authenticated: must be logged in ─────────────────────────────────

@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    """Returns the currently logged in user's own profile."""
    return user


@router.patch("/me", response_model=UserResponse)
def update_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Allows a user to update their own profile only."""
    update_data = user_in.model_dump(exclude_unset=True)
    
    # Security: explicitly block self-promotion
    forbidden_fields = {"role", "membership_status", "guest_allowance"}
    if any(field in update_data for field in forbidden_fields):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot self-modify administrative fields"
        )

    for field, val in update_data.items():
        if field == "password":
            user.set_password(val)
        else:
            setattr(user, field, val)
    
    db.commit()
    db.refresh(user)
    return user