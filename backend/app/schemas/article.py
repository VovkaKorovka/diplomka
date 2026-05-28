from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# =========================
# CREATE
# =========================
class ArticleCreate(BaseModel):
    title: str
    content: str
    culture_id: Optional[int] = None
    is_album: Optional[bool] = False


# =========================
# UPDATE
# =========================
class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    culture_id: Optional[int] = None
    is_album: Optional[bool] = None
    status: Optional[str] = None


# =========================
# RESPONSE
# =========================
class ArticleOut(BaseModel):
    id: int

    title: str
    content: str

    author_id: Optional[int] = None
    culture_id: Optional[int] = None

    status: str
    views: int

    is_album: bool = False

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True