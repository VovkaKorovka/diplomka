from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.genre import Genre
from app.schemas.genre import GenreCreate

router = APIRouter(prefix="/genres", tags=["Genres"])


# =========================
# SAFE HELPERS
# =========================
def clean(v: str):
    if v is None:
        return ""
    return v.strip()


def get_role(user):
    return getattr(getattr(user, "role", None), "name", None)


# =========================
# GET ALL GENRES
# =========================
@router.get("/")
def get_genres(db: Session = Depends(get_db)):

    genres = db.query(Genre).all()

    return [
        {
            "id": g.id,
            "name": g.name or ""
        }
        for g in genres
    ]


# =========================
# CREATE GENRE (ADMIN ONLY)
# =========================
@router.post("/")
def create_genre(
    data: GenreCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    role = get_role(user)

    if role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    name = clean(data.name)

    # 🔥 VALIDATION
    if not name:
        raise HTTPException(status_code=400, detail="Genre name required")

    if len(name) < 2:
        raise HTTPException(status_code=400, detail="Genre name too short")

    # 🔥 duplicate check
    exists = db.query(Genre).filter(Genre.name == name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Genre already exists")

    genre = Genre(name=name)

    db.add(genre)
    db.commit()
    db.refresh(genre)

    return {
        "id": genre.id,
        "name": genre.name
    }


# =========================
# GET CULTURES BY GENRE
# =========================
@router.get("/{genre_id}/cultures")
def get_cultures_by_genre(
    genre_id: int,
    db: Session = Depends(get_db)
):

    genre = db.query(Genre).filter(Genre.id == genre_id).first()

    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    cultures = getattr(genre, "cultures", [])

    return [
        {
            "id": c.id,
            "name": getattr(c, "title", "") or "",
            "country_id": getattr(c, "country_id", None)
        }
        for c in cultures
    ]