from pydantic import BaseModel
from typing import Optional


class InstrumentBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class InstrumentCreate(InstrumentBase):
    pass


class InstrumentResponse(InstrumentBase):
    id: int

    class Config:
        from_attributes = True