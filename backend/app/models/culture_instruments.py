from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base


class CultureInstrument(Base):
    __tablename__ = "culture_instruments"

    culture_id = Column(
        Integer,
        ForeignKey("music_cultures.id", ondelete="CASCADE"),
        primary_key=True
    )

    instrument_id = Column(
        Integer,
        ForeignKey("instruments.id", ondelete="CASCADE"),
        primary_key=True
    )