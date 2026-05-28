from pydantic import BaseModel
from typing import Optional


class CountryBase(BaseModel):
    name: str


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    name: Optional[str] = None


class CountryResponse(CountryBase):
    id: int

    class Config:
        from_attributes = True