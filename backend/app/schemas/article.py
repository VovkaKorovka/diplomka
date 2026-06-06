from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import Field

# =========================
# CREATE
# =========================
class ArticleCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=10)

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