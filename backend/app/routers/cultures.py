from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import get_current_user

from app.models.music_culture import MusicCulture
from app.models.country import Country

from app.schemas.culture import CultureCreate, CultureUpdate

router = APIRouter(prefix="/cultures", tags=["Music Cultures"])


# =========================
# 🔥 ERROR HANDLER
# =========================
def error(status: int, message: str, field: str | None = None):
    raise HTTPException(
        status_code=status,
        detail={
            "message": message,
            "field": field
        }
    )


# =========================
# 🧼 CLEANER
# =========================
def clean(v: str | None) -> str:
    return v.strip() if isinstance(v, str) else ""


# =========================
# 👮 ROLE
# =========================
def get_role(user):
    return getattr(getattr(user, "role", None), "name", None)


def require_roles(user, allowed: list[str]):
    role = get_role(user)
    if role not in allowed:
        error(403, "Forbidden")


# =========================
# 🧪 VALIDATION
# =========================
def validate_name(name: str):
    name = clean(name)

    if not name:
        error(400, "Culture name is required", "name")

    if len(name) < 2:
        error(400, "Culture name too short", "name")

    if len(name) > 150:
        error(400, "Culture name too long", "name")

    return name


# =========================
# 🌍 GET ALL CULTURES
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
# 📄 GET BY ID
# =========================
@router.get("/{culture_id}")
def get_culture(culture_id: int, db: Session = Depends(get_db)):

    c = db.query(MusicCulture).filter(MusicCulture.id == culture_id).first()

    if not c:
        error(404, "Culture not found")

    return {
        "id": c.id,
        "name": c.title or "",
        "country_id": c.country_id,
        "short_description": c.short_description or "",
        "history": c.history or "",
        "traditions": c.traditions or ""
    }


# =========================
# ➕ CREATE CULTURE
# =========================
@router.post("/")
def create_culture(
    data: CultureCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_roles(user, ["admin", "author"])

    name = validate_name(data.name)

    # country check
    country = db.query(Country).filter(Country.id == data.country_id).first()

    if not country:
        error(404, "Country not found", "country_id")

    # duplicate check (case-insensitive)
    exists = db.query(MusicCulture).filter(
        func.lower(MusicCulture.title) == name.lower()
    ).first()

    if exists:
        error(400, "Culture already exists", "name")

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
# ✏️ UPDATE CULTURE
# =========================
@router.put("/{culture_id}")
def update_culture(
    culture_id: int,
    data: CultureUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_roles(user, ["admin", "author"])

    c = db.query(MusicCulture).filter(MusicCulture.id == culture_id).first()

    if not c:
        error(404, "Culture not found")

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data:
        c.title = validate_name(update_data["name"])
        update_data.pop("name")

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
# ❌ DELETE CULTURE
# =========================
@router.delete("/{culture_id}")
def delete_culture(
    culture_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_roles(user, ["admin"])

    c = db.query(MusicCulture).filter(MusicCulture.id == culture_id).first()

    if not c:
        error(404, "Culture not found")

    db.delete(c)
    db.commit()

    return {
        "message": "deleted",
        "id": culture_id
    }