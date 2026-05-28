from pydantic import BaseModel
from typing import Optional, List


class CultureBase(BaseModel):
    country_id: int
    name: str  
    short_description: Optional[str] = None
    history: Optional[str] = None
    traditions: Optional[str] = None


class CultureCreate(CultureBase):
    genre_ids: List[int] = []
    instrument_ids: List[int] = []


class CultureUpdate(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = None
    history: Optional[str] = None
    traditions: Optional[str] = None


class CultureResponse(CultureBase):
    id: int

    class Config:
        from_attributes = True