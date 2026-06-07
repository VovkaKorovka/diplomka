from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.country import Country
from app.schemas.country import CountryCreate, CountryResponse

router = APIRouter(prefix="/countries", tags=["Countries"])


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
# 🧪 VALIDATION
# =========================
def validate_country_name(name: str):
    name = clean(name)

    if not name:
        error(400, "Country name is required", "name")

    if len(name) < 2:
        error(400, "Country name too short", "name")

    if len(name) > 100:
        error(400, "Country name too long", "name")

    return name


# =========================
# 👮 ADMIN CHECK
# =========================
def require_admin(user):
    role_name = getattr(getattr(user, "role", None), "name", None)
    if role_name != "admin":
        error(403, "Admin access required")


# =========================
# 🌍 GET ALL COUNTRIES
# =========================
@router.get("/")
def get_countries(db: Session = Depends(get_db)):

    countries = db.query(Country).all()

    return [
        {
            "id": c.id,
            "name": c.name or ""
        }
        for c in countries
    ]


# =========================
# 📄 GET BY ID
# =========================
@router.get("/{country_id}")
def get_country(country_id: int, db: Session = Depends(get_db)):

    country = db.query(Country).filter(Country.id == country_id).first()

    if not country:
        error(404, "Country not found")

    return {
        "id": country.id,
        "name": country.name or ""
    }


# =========================
# ➕ CREATE COUNTRY (ADMIN)
# =========================
@router.post("/", response_model=CountryResponse)
def create_country(
    data: CountryCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_admin(user)

    name = validate_country_name(data.name)

    # 🔥 duplicate check (case-insensitive)
    exists = db.query(Country).filter(
        func.lower(Country.name) == name.lower()
    ).first()

    if exists:
        error(400, "Country already exists", "name")

    country = Country(name=name)

    db.add(country)
    db.commit()
    db.refresh(country)

    return country


# =========================
# ❌ DELETE COUNTRY (ADMIN)
# =========================
@router.delete("/{country_id}")
def delete_country(
    country_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_admin(user)

    country = db.query(Country).filter(Country.id == country_id).first()

    if not country:
        error(404, "Country not found")

    db.delete(country)
    db.commit()

    return {
        "message": "deleted",
        "id": country_id
    }