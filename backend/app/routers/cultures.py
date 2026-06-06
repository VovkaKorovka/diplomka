from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user

from app.models.music_culture import MusicCulture
from app.models.country import Country

from app.schemas.culture import CultureCreate, CultureUpdate

router = APIRouter(prefix="/cultures", tags=["Music Cultures"])


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
# GET ALL CULTURES
# =========================
@router.get("/")
def get_cultures(db: Session = Depends(get_db)):

    cultures = db.query(MusicCulture).all()

    return [
        {
            "id": c.id,
            "name": c.title or "",
            "country_id": c.country_id,
            "short_description": c.short_description or "",
            "history": c.history or "",
            "traditions": c.traditions or ""
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
        "name": c.title or "",
        "country_id": c.country_id,
        "short_description": c.short_description or "",
        "history": c.history or "",
        "traditions": c.traditions or ""
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

    role = get_role(user)

    if role not in ["admin", "author"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    name = clean(data.name)

    # 🔥 VALIDATION
    if not name:
        raise HTTPException(status_code=400, detail="Culture name required")

    if len(name) < 2:
        raise HTTPException(status_code=400, detail="Culture name too short")

    country = db.query(Country).filter(Country.id == data.country_id).first()

    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    # 🔥 duplicate check
    exists = db.query(MusicCulture).filter(MusicCulture.title == name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Culture already exists")

    culture = MusicCulture(
        title=name,
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

    role = get_role(user)

    if role not in ["admin", "author"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    c = db.query(MusicCulture).filter(MusicCulture.id == culture_id).first()

    if not c:
        raise HTTPException(status_code=404, detail="Culture not found")

    update_data = data.model_dump(exclude_unset=True)

    # 🔥 clean name if exists
    if "name" in update_data:
        update_data["title"] = clean(update_data.pop("name"))

    for key, value in update_data.items():
        setattr(c, key, value)

    db.commit()
    db.refresh(c)

    return {
        "id": c.id,
        "name": c.title or "",
        "country_id": c.country_id,
        "short_description": c.short_description or "",
        "history": c.history or "",
        "traditions": c.traditions or ""
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

    role = get_role(user)

    if role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    c = db.query(MusicCulture).filter(MusicCulture.id == culture_id).first()

    if not c:
        raise HTTPException(status_code=404, detail="Culture not found")

    db.delete(c)
    db.commit()

    return {
        "message": "Culture deleted",
        "id": culture_id
    }