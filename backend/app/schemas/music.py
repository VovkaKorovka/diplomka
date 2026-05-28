from pydantic import BaseModel


# ➕ CREATE
class MusicCreate(BaseModel):
    title: str
    youtube_url: str
    position: int = 0


# 📤 RESPONSE
class MusicOut(BaseModel):
    id: int
    article_id: int
    title: str
    youtube_url: str
    position: int

    class Config:
        from_attributes = True