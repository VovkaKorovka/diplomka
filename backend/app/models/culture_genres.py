from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base


class CultureGenre(Base):
    __tablename__ = "culture_genres"

    culture_id = Column(
        Integer,
        ForeignKey("music_cultures.id", ondelete="CASCADE"),
        primary_key=True
    )

    genre_id = Column(
        Integer,
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True
    )