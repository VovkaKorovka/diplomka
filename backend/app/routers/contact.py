from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.contact import ContactCreate
from app.models.contact_message import ContactMessage

router = APIRouter(prefix="/contact", tags=["Contact"])


# =========================
# SAFE HELPERS
# =========================
def clean(v: str):
    if v is None:
        return ""
    return v.strip()


def is_valid_email(email: str):
    return isinstance(email, str) and "@" in email and "." in email


# =========================
# CREATE CONTACT
# =========================
@router.post("/")
def create_contact(data: ContactCreate, db: Session = Depends(get_db)):

    email = clean(data.email)
    message = clean(data.message)

    # 🔥 VALIDATION
    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email")

    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if len(message) < 5:
        raise HTTPException(status_code=400, detail="Message too short")

    contact = ContactMessage(
        email=email,
        message=message
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return {
        "message": "saved",
        "id": contact.id
    }


# =========================
# GET CONTACTS
# =========================
@router.get("/")
def get_contacts(db: Session = Depends(get_db)):

    contacts = (
        db.query(ContactMessage)
        .order_by(ContactMessage.id.desc())
        .all()
    )

    return [
        {
            "id": c.id,
            "email": c.email or "",
            "message": c.message or ""
        }
        for c in contacts
    ]


# =========================
# DELETE CONTACT
# =========================
@router.delete("/{id}")
def delete_contact(id: int, db: Session = Depends(get_db)):

    obj = db.query(ContactMessage).filter(ContactMessage.id == id).first()

    if not obj:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(obj)
    db.commit()

    return {
        "message": "deleted",
        "id": id
    }