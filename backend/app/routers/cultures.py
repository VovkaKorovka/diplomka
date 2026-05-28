from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user

from app.models.music_culture import MusicCulture
from app.models.country import Country

from app.schemas.culture import CultureCreate, CultureUpdate

router = APIRouter(prefix="/cultures", tags=["Music Cultures"])


# =========================
# GET ALL CULTURES
# =========================
@router.get("/")
def get_cultures(db: Session = Depends(get_db)):
    cultures = db.query(MusicCulture).all()

    return [
        {
            "id": c.id,
            "name": c.title,   # 🔥 FIX: фронт очікує name
            "country_id": c.country_id,
            "short_description": c.short_description,
            "history": c.history,
            "traditions": c.traditions
        }
        for c in cultures
    ]


# =========================
# GET BY ID
# =========================
@router.get("/{culture_id}")
def get_culture(culture_id: int, db: Session = Depends(get_db)):
    c = db.query(MusicCulture).filter(MusicCulture.id == culture_id).first()

    if not c:
        raise HTTPException(status_code=404, detail="Culture not found")

    return {
        "id": c.id,
        "name": c.title,
        "country_id": c.country_id,
        "short_description": c.short_description,
        "history": c.history,
        "traditions": c.traditions
    }


# =========================
# CREATE CULTURE
# =========================
@router.post("/")
def create_culture(
    data: CultureCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if user.role.name not in ["admin", "author"]:
        raise HTTPException(status_code=403)

    country = db.query(Country).filter(Country.id == data.country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    culture = MusicCulture(
        title=data.name,   # 🔥 FIX HERE
        country_id=data.country_id
    )

    db.add(culture)
    db.commit()
    db.refresh(culture)

    return {
        "id": culture.id,
        "name": culture.title,
        "country_id": culture.country_id
    }


# =========================
# UPDATE CULTURE
# =========================
@router.put("/{culture_id}")
def update_culture(
    culture_id: int,
    data: CultureUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role.name not in ["admin", "author"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    c = db.query(MusicCulture).filter(MusicCulture.id == culture_id).first()

    if not c:
        raise HTTPException(status_code=404, detail="Culture not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(c, key, value)

    db.commit()
    db.refresh(c)

    return {
        "id": c.id,
        "name": c.title,
        "country_id": c.country_id,
        "short_description": c.short_description,
        "history": c.history,
        "traditions": c.traditions
    }


# =========================
# DELETE CULTURE
# =========================
@router.delete("/{culture_id}")
def delete_culture(
    culture_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    c = db.query(MusicCulture).filter(MusicCulture.id == culture_id).first()

    if not c:
        raise HTTPException(status_code=404, detail="Culture not found")

    db.delete(c)
    db.commit()

    return {"message": "Culture deleted"}