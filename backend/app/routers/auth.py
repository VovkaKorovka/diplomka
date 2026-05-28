from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.role import Role

from app.schemas.user import UserCreate
from app.schemas.auth import LoginSchema

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# =========================
# REGISTER
# =========================
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    role_user = db.query(Role).filter(Role.name == "user").first()

    if not role_user:
        raise HTTPException(
            status_code=500,
            detail="Default role 'user' not found in DB"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        role_id=role_user.id,
        is_active=True   # 🔥 IMPORTANT
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(
        data={
            "user_id": new_user.id,
            "email": new_user.email,
            "role": role_user.name
        }
    )

    return {
        "success": True,
        "message": "User registered successfully",
        "access_token": token,
        "token_type": "bearer",
        "role": role_user.name
    }


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    role_name = user.role.name if user.role else "user"  # safety

    token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "role": role_name
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": role_name
    }