from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)

    # =====================
    # MAIN FIELDS
    # =====================

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    status = Column(String(20), default="draft")
    views = Column(Integer, default=0)

    # 🔥 FIX FOR YOUR FRONTEND (is_album)
    is_album = Column(Boolean, default=True)

    # =====================
    # FOREIGN KEYS
    # =====================

    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    culture_id = Column(
        Integer,
        ForeignKey("music_cultures.id", ondelete="CASCADE"),
        nullable=True
    )

    # =====================
    # TIMESTAMPS
    # =====================

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # =====================
    # RELATIONS (SAFE + SYNCED)
    # =====================

    author = relationship(
        "User",
        back_populates="articles"
    )

    culture = relationship(
        "MusicCulture",
        back_populates="articles"
    )

    comments = relationship(
        "Comment",
        back_populates="article",
        cascade="all, delete-orphan"
    )

    ratings = relationship(
        "Rating",
        back_populates="article",
        cascade="all, delete-orphan"
    )

    favorites = relationship(
        "Favorite",
        back_populates="article",
        cascade="all, delete-orphan"
    )

    # 🔥 MUSIC (IMPORTANT FIX)
    music = relationship(
        "Music",
        back_populates="article",
        cascade="all, delete-orphan"
    )