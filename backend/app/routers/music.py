from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.music import Music
from app.models.article import Article
from app.schemas.music import MusicCreate, MusicOut
from app.core.deps import require_admin


router = APIRouter(prefix="/music", tags=["Music"])


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
        raise HTTPException(status_code=404, detail="Article not found")

    if not article.is_album:
        raise HTTPException(status_code=400, detail="Article is not album")

    music = Music(
        article_id=article_id,
        title=data.title,
        youtube_url=data.youtube_url,
        position=data.position
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
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(music)
    db.commit()

    return {"message": "deleted"}


# =========================
# ✏️ UPDATE MUSIC (OPTIONAL)
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
        raise HTTPException(status_code=404, detail="Not found")

    music.title = data.title
    music.youtube_url = data.youtube_url
    music.position = data.position

    db.commit()
    db.refresh(music)

    return music