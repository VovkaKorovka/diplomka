from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship   # <-- ВАЖЛИВО
from app.core.database import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"))

    rating = Column(Integer)

    user = relationship("User", back_populates="ratings")
    article = relationship("Article", back_populates="ratings")