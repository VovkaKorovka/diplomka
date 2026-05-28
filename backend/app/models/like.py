from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"))