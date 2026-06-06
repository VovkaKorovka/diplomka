from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.country import Country
from app.schemas.country import CountryCreate, CountryResponse

router = APIRouter(prefix="/countries", tags=["Countries"])


# =========================
# SAFE HELPERS
# =========================
def clean(v: str):
    if v is None:
        return ""
    return v.strip()


# =========================
# GET ALL COUNTRIES
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
# GET BY ID
# =========================
@router.get("/{country_id}")
def get_country(country_id: int, db: Session = Depends(get_db)):

    country = db.query(Country).filter(Country.id == country_id).first()

    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    return {
        "id": country.id,
        "name": country.name or ""
    }


# =========================
# CREATE (ADMIN ONLY)
# =========================
@router.post("/", response_model=CountryResponse)
def create_country(
    data: CountryCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    role_name = getattr(getattr(user, "role", None), "name", None)

    if role_name != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create country")

    name = clean(data.name)

    # 🔥 VALIDATION
    if not name:
        raise HTTPException(status_code=400, detail="Country name required")

    if len(name) < 2:
        raise HTTPException(status_code=400, detail="Country name too short")

    # 🔥 duplicate check
    exists = db.query(Country).filter(Country.name == name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Country already exists")

    country = Country(name=name)

    db.add(country)
    db.commit()
    db.refresh(country)

    return country


# =========================
# DELETE (ADMIN ONLY)
# =========================
@router.delete("/{country_id}")
def delete_country(
    country_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    role_name = getattr(getattr(user, "role", None), "name", None)

    if role_name != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    country = db.query(Country).filter(Country.id == country_id).first()

    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    db.delete(country)
    db.commit()

    return {
        "message": "Country deleted",
        "id": country_id
    }