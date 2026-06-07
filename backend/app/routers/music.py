from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.music import Music
from app.models.article import Article
from app.schemas.music import MusicCreate, MusicOut
from app.core.deps import require_admin

router = APIRouter(prefix="/music", tags=["Music"])


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
def clean(v: str | None) -> str:
    return v.strip() if isinstance(v, str) else ""


# =========================
# 🧪 VALIDATION
# =========================
def validate_title(title: str):
    title = clean(title)

    if not title:
        error(400, "Title is required", "title")

    if len(title) < 2:
        error(400, "Title too short", "title")

    if len(title) > 200:
        error(400, "Title too long", "title")

    return title


def validate_url(url: str):
    url = clean(url)

    if not url:
        error(400, "YouTube URL is required", "youtube_url")

    if "http" not in url:
        error(400, "Invalid YouTube URL", "youtube_url")

    return url


def validate_position(pos):
    try:
        pos = int(pos)
    except:
        error(400, "Position must be a number", "position")

    if pos < 0:
        error(400, "Position cannot be negative", "position")

    return pos


# =========================
# 🎵 GET MUSIC BY ARTICLE
# =========================
@router.get("/{article_id}", response_model=list[MusicOut])
def get_music(article_id: int, db: Session = Depends(get_db)):

    return (
        db.query(Music)
        .filter(Music.article_id == article_id)
        .order_by(Music.position)
        .all()
    )


# =========================
# ➕ ADD MUSIC
# =========================
@router.post("/{article_id}", response_model=MusicOut)
def add_music(
    article_id: int,
    data: MusicCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        error(404, "Article not found")

    if not article.is_album:
        error(400, "This article is not an album")

    title = validate_title(data.title)
    youtube_url = validate_url(data.youtube_url)
    position = validate_position(data.position)

    music = Music(
        article_id=article_id,
        title=title,
        youtube_url=youtube_url,
        position=position
    )

    db.add(music)
    db.commit()
    db.refresh(music)

    return music


# =========================
# ❌ DELETE MUSIC
# =========================
@router.delete("/{music_id}")
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

    return {"message": "deleted", "id": music_id}


# =========================
# ✏️ UPDATE MUSIC
# =========================
@router.put("/{music_id}", response_model=MusicOut)
def update_music(
    music_id: int,
    data: MusicCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    music = db.query(Music).filter(Music.id == music_id).first()

    if not music:
        error(404, "Music not found")

    music.title = validate_title(data.title)
    music.youtube_url = validate_url(data.youtube_url)
    music.position = validate_position(data.position)

    db.commit()
    db.refresh(music)

    return music