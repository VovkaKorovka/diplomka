from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.models.article import Article
from app.models.music_culture import MusicCulture
from app.models.music import Music
from app.models.rating import Rating

from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleOut
from app.core.deps import get_current_user, require_admin

router = APIRouter(prefix="/articles", tags=["Articles"])


# =========================
# 🌍 ALL ARTICLES
# =========================
@router.get("/", response_model=list[ArticleOut])
def get_articles(
    db: Session = Depends(get_db),
    limit: int = Query(20, le=100),
    offset: int = 0
):
    return (
        db.query(Article)
        .order_by(desc(Article.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )


# =========================
# 🔍 SEARCH
# =========================
@router.get("/search", response_model=list[ArticleOut])
def search_articles(q: str, db: Session = Depends(get_db)):
    return (
        db.query(Article)
        .filter(Article.title.ilike(f"%{q}%"))
        .limit(50)
        .all()
    )


# =========================
# 🆕 LATEST
# =========================
@router.get("/latest", response_model=list[ArticleOut])
def latest_articles(db: Session = Depends(get_db)):
    return (
        db.query(Article)
        .order_by(desc(Article.created_at))
        .limit(10)
        .all()
    )


# =========================
# 🔥 POPULAR
# =========================
@router.get("/popular", response_model=list[ArticleOut])
def popular_articles(db: Session = Depends(get_db)):
    return (
        db.query(Article)
        .order_by(desc(Article.views))
        .limit(10)
        .all()
    )


# =========================
# 🌍 BY COUNTRY
# =========================
@router.get("/by-country/{country_id}", response_model=list[ArticleOut])
def by_country(country_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Article)
        .join(MusicCulture, Article.culture_id == MusicCulture.id)
        .filter(MusicCulture.country_id == country_id)
        .all()
    )


# =========================
# 📄 GET BY ID
# =========================
@router.get("/{article_id}", response_model=ArticleOut)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.views += 1
    db.commit()

    return article


# =========================
# 🎵 GET MUSIC
# =========================
@router.get("/{article_id}/music")
def get_article_music(article_id: int, db: Session = Depends(get_db)):

    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404)

    return (
        db.query(Music)
        .filter(Music.article_id == article_id)
        .order_by(Music.position)
        .all()
    )


# =========================
# ➕ ADD MUSIC
# =========================
@router.post("/{article_id}/music")
def add_music_to_article(
    article_id: int,
    data: dict,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404)

    if not article.is_album:
        raise HTTPException(status_code=400, detail="Not an album")

    title = data.get("title", "").strip()
    youtube_url = data.get("youtube_url", "").strip()

    if not title or not youtube_url:
        raise HTTPException(status_code=400, detail="Empty fields")

    music = Music(
        article_id=article_id,
        title=title,
        youtube_url=youtube_url,
        position=data.get("position", 0)
    )

    db.add(music)
    db.commit()
    db.refresh(music)

    return music


# =========================
# ❌ DELETE MUSIC
# =========================
@router.delete("/music/{music_id}")
def delete_music(
    music_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    music = db.query(Music).filter(Music.id == music_id).first()

    if not music:
        raise HTTPException(status_code=404)

    db.delete(music)
    db.commit()

    return {"message": "deleted"}


# =========================
# 🆕 CREATE ARTICLE
# =========================
@router.post("/", response_model=ArticleOut)
def create_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    title = article.title.strip()
    content = article.content.strip()

    if not title or len(title) < 3:
        raise HTTPException(status_code=400, detail="Title too short")

    if not content or len(content) < 10:
        raise HTTPException(status_code=400, detail="Content too short")

    new_article = Article(
        title=title,
        content=content,
        author_id=user.id,
        culture_id=article.culture_id,
        is_album=bool(article.is_album),
        status="published"
    )

    db.add(new_article)
    db.commit()
    db.refresh(new_article)

    return new_article


# =========================
# ✏️ UPDATE ARTICLE
# =========================
@router.put("/{article_id}", response_model=ArticleOut)
def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404)

    if article.author_id != user.id and user.role.name != "admin":
        raise HTTPException(status_code=403)

    if article_data.title is not None:
        title = article_data.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        article.title = title

    if article_data.content is not None:
        content = article_data.content.strip()
        if not content:
            raise HTTPException(status_code=400, detail="Content cannot be empty")
        article.content = content

    if article_data.culture_id is not None:
        article.culture_id = article_data.culture_id

    if article_data.is_album is not None:
        article.is_album = article_data.is_album

    if article_data.status is not None:
        article.status = article_data.status

    db.commit()
    db.refresh(article)

    return article


# =========================
# 🗑 DELETE ARTICLE
# =========================
@router.delete("/{article_id}")
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404)

    db.delete(article)
    db.commit()

    return {"message": "deleted"}


# =========================
# 🚀 PUBLISH
# =========================
@router.patch("/{article_id}/publish")
def publish(article_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):

    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404)

    article.status = "published"
    db.commit()

    return {"message": "published"}


# =========================
# 💤 DRAFT
# =========================
@router.patch("/{article_id}/draft")
def draft(article_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):

    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404)

    article.status = "draft"
    db.commit()

    return {"message": "drafted"}


# =========================
# ⭐ RATING STATS
# =========================
@router.get("/{article_id}/rating-stats")
def get_rating_stats(article_id: int, db: Session = Depends(get_db)):

    result = db.query(
        func.count(Rating.id),
        func.avg(Rating.rating)
    ).filter(Rating.article_id == article_id).first()

    return {
        "count": result[0] or 0,
        "avg": float(result[1]) if result[1] else 0
    }