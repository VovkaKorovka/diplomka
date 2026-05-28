from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.instrument import Instrument
from app.schemas.instrument import InstrumentCreate

router = APIRouter(prefix="/instruments", tags=["Instruments"])


# =========================
# GET ALL INSTRUMENTS
# =========================
@router.get("/")
def get_instruments(db: Session = Depends(get_db)):
    return db.query(Instrument).all()


# =========================
# GET BY ID
# =========================
@router.get("/{instrument_id}")
def get_instrument(instrument_id: int, db: Session = Depends(get_db)):
    instrument = db.query(Instrument).filter(
        Instrument.id == instrument_id
    ).first()

    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    return instrument


# =========================
# CREATE (ADMIN ONLY)
# =========================
@router.post("/")
def create_instrument(
    data: InstrumentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    instrument = Instrument(**data.model_dump())

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    return instrument