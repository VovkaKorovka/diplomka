from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    image_url = Column(String(255))

    cultures = relationship(
        "MusicCulture",
        secondary="culture_instruments",
        back_populates="instruments"
    )