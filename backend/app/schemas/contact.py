from pydantic import BaseModel, EmailStr

class ContactCreate(BaseModel):
    email: EmailStr
    message: str