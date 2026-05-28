from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.genre import Genre
from app.schemas.genre import GenreCreate

router = APIRouter(prefix="/genres", tags=["Genres"])


# =========================
# GET ALL GENRES
# =========================
@router.get("/")
def get_genres(db: Session = Depends(get_db)):
    return db.query(Genre).all()


# =========================
# CREATE GENRE (ADMIN ONLY)
# =========================
@router.post("/")
def create_genre(
    data: GenreCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    genre = Genre(**data.model_dump())

    db.add(genre)
    db.commit()
    db.refresh(genre)

    return genre


# =========================
# GET CULTURES BY GENRE
# =========================
@router.get("/{genre_id}/cultures")
def get_cultures_by_genre(
    genre_id: int,
    db: Session = Depends(get_db)
):
    genre = db.query(Genre).filter(
        Genre.id == genre_id
    ).first()

    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    # 🔥 safe access (щоб не падало якщо relationship кривий)
    return getattr(genre, "cultures", [])