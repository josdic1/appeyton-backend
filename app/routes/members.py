# app/routes/members.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.member import Member
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(
    payload: MemberCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    m = Member(
        user_id=user.id,
        created_by_user_id=user.id,
        name=payload.name,
        relation=payload.relation,
        dietary_restrictions=payload.dietary_restrictions,
        meta=payload.meta,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.get("", response_model=list[MemberResponse])
def list_members(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.query(Member).filter(Member.user_id == user.id).order_by(Member.id.asc()).all()


@router.patch("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: int,
    payload: MemberUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    m = db.query(Member).filter(Member.id == member_id, Member.user_id == user.id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Member not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(m, k, v)

    db.commit()
    db.refresh(m)
    return m


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    m = db.query(Member).filter(Member.id == member_id, Member.user_id == user.id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(m)
    db.commit()
    return None