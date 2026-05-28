from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    preferred_language: str | None = None


class AvatarUpdate(BaseModel):
    avatar_url: str


class UserResponse(UserBase):
    id: int
    role_id: int
    avatar_url: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True