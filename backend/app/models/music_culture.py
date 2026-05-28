from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

from app.models.culture_genres import CultureGenre
from app.models.culture_instruments import CultureInstrument


class MusicCulture(Base):
    __tablename__ = "music_cultures"

    id = Column(Integer, primary_key=True)

    country_id = Column(
        Integer,
        ForeignKey("countries.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(String(200), nullable=False)
    short_description = Column(Text)
    history = Column(Text)
    traditions = Column(Text)

    # =====================
    # RELATIONS
    # =====================

    country = relationship(
        "Country",
        back_populates="cultures"
    )

    genres = relationship(
        "Genre",
        secondary="culture_genres",   # 👈 OK (table name)
        back_populates="cultures",
        lazy="select"
    )

    instruments = relationship(
        "Instrument",
        secondary="culture_instruments",  # 👈 OK (table name)
        back_populates="cultures",
        lazy="select"
    )

    articles = relationship(
        "Article",
        back_populates="culture",
        cascade="all, delete"
    )