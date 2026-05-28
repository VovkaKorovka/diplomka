from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    cultures = relationship(
        "MusicCulture",
        back_populates="country",
        cascade="all, delete"
    )