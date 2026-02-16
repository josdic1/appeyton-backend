# app/routes/members.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.member import Member
from app.models.user import User
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(
    payload: MemberCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Check if "self" already exists
    if payload.relation and payload.relation.lower() == "self":
        existing_self = db.query(Member).filter(
            Member.user_id == user.id,
            Member.relation.ilike("self")
        ).first()
        if existing_self:
            raise HTTPException(
                status_code=400,
                detail="You already have a 'self' family member. Only one allowed."
            )
    
    # Check duplicate name
    existing_name = db.query(Member).filter(
        Member.user_id == user.id,
        Member.name == payload.name
    ).first()
    if existing_name:
        raise HTTPException(
            status_code=400,
            detail=f"Family member named '{payload.name}' already exists"
        )
    
    m = Member(
        user_id=user.id,
        created_by_user_id=user.id,
        name=payload.name,
        relation=payload.relation,
        dietary_restrictions=payload.dietary_restrictions,
        meta=payload.meta,
    )
    db.add(m)
    
    try:
        db.commit()
        db.refresh(m)
        return m
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Member already exists")


@router.get("", response_model=list[MemberResponse])
def list_members(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.query(Member).filter(Member.user_id == user.id).order_by(Member.id.asc()).all()


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    m = db.query(Member).filter(Member.id == member_id, Member.user_id == user.id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Member not found")
    return m


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

    # If changing relation to "self", check no other self exists
    if payload.relation and payload.relation.lower() == "self":
        existing_self = db.query(Member).filter(
            Member.user_id == user.id,
            Member.relation.ilike("self"),
            Member.id != member_id
        ).first()
        if existing_self:
            raise HTTPException(
                status_code=400,
                detail="You already have a 'self' family member"
            )
    
    # If changing name, check duplicate
    if payload.name and payload.name != m.name:
        existing_name = db.query(Member).filter(
            Member.user_id == user.id,
            Member.name == payload.name,
            Member.id != member_id
        ).first()
        if existing_name:
            raise HTTPException(
                status_code=400,
                detail=f"Family member named '{payload.name}' already exists"
            )

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