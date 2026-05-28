from pydantic import BaseModel
from typing import Optional


class CommentCreate(BaseModel):
    article_id: int
    content: str


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    is_hidden: Optional[bool] = None


class CommentResponse(BaseModel):
    id: int
    user_id: int
    article_id: int
    content: str
    is_hidden: bool

    class Config:
        from_attributes = True