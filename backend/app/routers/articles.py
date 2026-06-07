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
# 🔥 ERROR HANDLER
# =========================
def error(status: int, message: str, field: str | None = None):
    raise HTTPException(
        status_code=status,
        detail={
            "message": message,
            "field": field
        }
    )


# =========================
# 🧼 CLEANER
# =========================
def clean(value: str | None) -> str:
    return value.strip() if isinstance(value, str) else ""


# =========================
# 🧪 VALIDATORS
# =========================
def validate_title(title: str):
    title = clean(title)

    if not title:
        error(400, "Title is required", "title")

    if len(title) < 3:
        error(400, "Title must be at least 3 characters", "title")

    if len(title) > 200:
        error(400, "Title is too long (max 200 chars)", "title")

    return title


def validate_content(content: str):
    content = clean(content)

    if not content:
        error(400, "Content is required", "content")

    if len(content) < 10:
        error(400, "Content must be at least 10 characters", "content")

    if len(content) > 50000:
        error(400, "Content is too long", "content")

    return content


def validate_url(url: str):
    url = clean(url)

    if not url:
        error(400, "YouTube URL is required", "youtube_url")

    if "http" not in url:
        error(400, "Invalid URL format", "youtube_url")

    return url


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

    q = clean(q)
    if not q:
        error(400, "Search query is required", "q")

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
        error(404, "Article not found")

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
        error(404, "Article not found")

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
        error(404, "Article not found")

    if not article.is_album:
        error(400, "This article is not an album")

    title = validate_title(data.get("title"))
    youtube_url = validate_url(data.get("youtube_url"))

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
        error(404, "Music not found")

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

    title = validate_title(article.title)
    content = validate_content(article.content)

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
        error(404, "Article not found")

    if article.author_id != user.id and user.role.name != "admin":
        error(403, "Not allowed to edit this article")

    if article_data.title is not None:
        article.title = validate_title(article_data.title)

    if article_data.content is not None:
        article.content = validate_content(article_data.content)

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
        error(404, "Article not found")

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
        error(404, "Article not found")

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
        error(404, "Article not found")

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