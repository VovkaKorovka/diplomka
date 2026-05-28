from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.country import Country
from app.schemas.country import CountryCreate, CountryUpdate, CountryResponse
router = APIRouter(prefix="/countries", tags=["Countries"])


# =========================
# GET ALL COUNTRIES
# =========================
@router.get("/")
def get_countries(db: Session = Depends(get_db)):
    return db.query(Country).all()


# =========================
# GET BY ID
# =========================
@router.get("/{country_id}")
def get_country(country_id: int, db: Session = Depends(get_db)):
    country = db.query(Country).filter(Country.id == country_id).first()

    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    return country


# =========================
# CREATE (ADMIN ONLY)
# =========================
@router.post("/", response_model=CountryResponse)
def create_country(
    data: CountryCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    role_name = getattr(user.role, "name", None)

    if role_name != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create country")

    country = Country(**data.model_dump())

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
    if user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    country = db.query(Country).filter(Country.id == country_id).first()

    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    db.delete(country)
    db.commit()

    return {"message": "Country deleted"}