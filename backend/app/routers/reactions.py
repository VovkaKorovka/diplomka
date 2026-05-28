from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.rating import Rating
from app.models.like import Like
from app.models.article import Article
from app.core.deps import get_current_user

router = APIRouter(prefix="/reactions", tags=["Reactions"])


# =========================
# ⭐ RATE
# =========================
@router.post("/rate")
def rate_article(
    article_id: int = Query(...),
    rating: int = Query(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")

    existing = db.query(Rating).filter(
        Rating.article_id == article_id,
        Rating.user_id == user.id
    ).first()

    if existing:
        existing.rating = rating
    else:
        db.add(Rating(
            article_id=article_id,
            user_id=user.id,
            rating=rating
        ))

    db.commit()
    return {"message": "rated"}


# =========================
# ❤️ LIKE TOGGLE
# =========================
@router.post("/like")
def like_article(
    article_id: int = Query(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    existing = db.query(Like).filter(
        Like.article_id == article_id,
        Like.user_id == user.id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"message": "unliked"}

    db.add(Like(
        article_id=article_id,
        user_id=user.id
    ))

    db.commit()
    return {"message": "liked"}


# =========================
# ❤️ MY LIKES
# =========================
@router.get("/my-likes")
def get_my_likes(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    likes = db.query(Like).filter(
        Like.user_id == user.id
    ).all()

    result = []

    for like in likes:
        article = db.query(Article).filter(
            Article.id == like.article_id
        ).first()

        if article:
            result.append({
                "id": article.id,
                "title": article.title,
                "content": article.content
            })

    return result


# =========================
# 📊 RATING STATS (FIXED PATH)
# =========================
@router.get("/rating-stats")
def get_rating_stats(
    article_id: int,
    db: Session = Depends(get_db)
):

    result = db.query(
        func.count(Rating.id),
        func.avg(Rating.rating)
    ).filter(Rating.article_id == article_id).first()

    return {
        "count": result[0] or 0,
        "avg": float(result[1]) if result[1] else 0
    }