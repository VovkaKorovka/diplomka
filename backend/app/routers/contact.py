from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.contact import ContactCreate
from app.models.contact_message import ContactMessage

router = APIRouter(prefix="/contact", tags=["Contact"])


@router.post("/")
def create_contact(data: ContactCreate, db: Session = Depends(get_db)):
    contact = ContactMessage(
        email=data.email,
        message=data.message
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return {"message": "saved", "id": contact.id}


@router.get("/")
def get_contacts(db: Session = Depends(get_db)):
    return db.query(ContactMessage).order_by(ContactMessage.id.desc()).all()


@router.delete("/{id}")
def delete_contact(id: int, db: Session = Depends(get_db)):
    obj = db.query(ContactMessage).filter(ContactMessage.id == id).first()

    if not obj:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(obj)
    db.commit()

    return {"message": "deleted"}