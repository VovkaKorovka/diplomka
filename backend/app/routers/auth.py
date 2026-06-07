from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

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
# HELPERS
# =========================
def clean_str(value: str):
    return value.strip() if value else ""


# =========================
# REGISTER
# =========================
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    username = clean_str(user.username)
    email = clean_str(user.email).lower()
    password = clean_str(user.password)

    # -------------------------
    # VALIDATION
    # -------------------------
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username too short")

    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password too short")

    if "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email")

    # -------------------------
    # CHECK USERNAME EXISTS
    # -------------------------
    existing_username = db.query(User).filter(
        func.lower(User.username) == username.lower()
    ).first()

    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    # -------------------------
    # CHECK EMAIL EXISTS
    # -------------------------
    existing_email = db.query(User).filter(
        func.lower(User.email) == email
    ).first()

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    # -------------------------
    # ROLE CHECK
    # -------------------------
    role_user = db.query(Role).filter(Role.name == "user").first()

    if not role_user:
        raise HTTPException(
            status_code=500,
            detail="Default role 'user' not found in DB"
        )

    # -------------------------
    # CREATE USER
    # -------------------------
    new_user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role_id=role_user.id,
        is_active=True
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

    email = clean_str(data.email).lower()
    password = clean_str(data.password)

    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password required"
        )

    user = db.query(User).filter(
        func.lower(User.email) == email
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is banned")

    role_name = user.role.name if user.role else "user"

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