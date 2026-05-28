from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Music(Base):
    __tablename__ = "music"

    id = Column(Integer, primary_key=True, index=True)

    article_id = Column(
        Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(String(255), nullable=False)
    youtube_url = Column(Text, nullable=False)

    position = Column(Integer, default=0)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # relation back
    article = relationship("Article", back_populates="music")