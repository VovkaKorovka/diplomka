from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.instrument import Instrument
from app.schemas.instrument import InstrumentCreate

router = APIRouter(prefix="/instruments", tags=["Instruments"])


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
# GET ALL INSTRUMENTS
# =========================
@router.get("/")
def get_instruments(db: Session = Depends(get_db)):

    instruments = db.query(Instrument).all()

    return [
        {
            "id": i.id,
            "name": i.name or ""
        }
        for i in instruments
    ]


# =========================
# GET BY ID
# =========================
@router.get("/{instrument_id}")
def get_instrument(instrument_id: int, db: Session = Depends(get_db)):

    instrument = (
        db.query(Instrument)
        .filter(Instrument.id == instrument_id)
        .first()
    )

    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    return {
        "id": instrument.id,
        "name": instrument.name or ""
    }


# =========================
# CREATE (ADMIN ONLY)
# =========================
@router.post("/")
def create_instrument(
    data: InstrumentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    role = get_role(user)

    if role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    name = clean(data.name)

    # 🔥 VALIDATION
    if not name:
        raise HTTPException(status_code=400, detail="Instrument name required")

    if len(name) < 2:
        raise HTTPException(status_code=400, detail="Instrument name too short")

    # 🔥 duplicate check
    exists = db.query(Instrument).filter(Instrument.name == name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Instrument already exists")

    instrument = Instrument(name=name)

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    return {
        "id": instrument.id,
        "name": instrument.name
    }