from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user

from app.models.user import User
from app.models.article import Article
from app.models.favorite import Favorite
from app.models.like import Like

from app.schemas.user import UserUpdate, AvatarUpdate

router = APIRouter(prefix="/users", tags=["Users"])


# =========================
# HELPER
# =========================
def require_active_user(user: User):
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is banned")

def require_active_user(current_user=Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="User is banned")
    return current_user

# =========================
# GET CURRENT USER
# =========================
@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": getattr(current_user.role, "name", None),
        "avatar_url": current_user.avatar_url,
        "preferred_language": current_user.preferred_language,
        "is_active": current_user.is_active
    }


# =========================
# GET ALL USERS (ADMIN / MODERATOR)
# =========================
@router.get("/")
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_active_user),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    require_active_user(current_user)

    if current_user.role.name not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    users = db.query(User).offset(offset).limit(limit).all()

    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": getattr(u.role, "name", None),
            "avatar_url": u.avatar_url,
            "created_at": u.created_at,
            "is_active": u.is_active
        }
        for u in users
    ]


# =========================
# GET USER PROFILE
# =========================
@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_active_user(current_user)

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is banned")

    if current_user.role.name not in ["admin", "moderator"] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {
        "id": user.id,
        "username": user.username,
        "avatar_url": user.avatar_url,
        "role": getattr(user.role, "name", None),
        "created_at": user.created_at,
        "is_active": user.is_active
    }


# =========================
# UPDATE PROFILE
# =========================
@router.put("/me")
def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_active_user(current_user)

    if data.username:
        existing = db.query(User).filter(User.username == data.username).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = data.username

    if data.preferred_language:
        current_user.preferred_language = data.preferred_language

    db.commit()
    db.refresh(current_user)

    return {"message": "Profile updated"}


# =========================
# UPDATE AVATAR
# =========================
@router.put("/avatar")
def update_avatar(
    data: AvatarUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_active_user(current_user)

    current_user.avatar_url = data.avatar_url

    db.commit()
    db.refresh(current_user)

    return {"message": "Avatar updated"}


# =========================
# USER ARTICLES
# =========================
@router.get("/{user_id}/articles")
def get_user_articles(
    user_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(20, le=50),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user)
):
    require_active_user(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")

    articles = (
        db.query(Article)
        .filter(Article.author_id == user_id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": a.id,
            "title": a.title,
            "status": a.status,
            "created_at": a.created_at
        }
        for a in articles
    ]


# =========================
# USER FAVORITES
# =========================
@router.get("/{user_id}/favorites")
def get_user_favorites(
    user_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(20, le=50),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user)
):
    require_active_user(current_user)

    favorites = (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": f.id,
            "article_id": f.article_id,
            "created_at": getattr(f, "created_at", None)
        }
        for f in favorites
    ]


# =========================
# BAN USER
# =========================
@router.patch("/{user_id}/ban")
def ban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_active_user(current_user)

    if current_user.role.name not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot ban yourself")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    return {"message": "User banned"}


# =========================
# UNBAN USER
# =========================
@router.patch("/{user_id}/unban")
def unban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_active_user(current_user)

    if current_user.role.name not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.commit()

    return {"message": "User unbanned"}


# =========================
# MY LIKES
# =========================
@router.get("/me/likes")
def my_likes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    require_active_user(current_user)

    likes = db.query(Like).filter(
        Like.user_id == current_user.id
    ).all()

    return [
        {
            "id": l.id,
            "article_id": l.article_id
        }
        for l in likes
    ]