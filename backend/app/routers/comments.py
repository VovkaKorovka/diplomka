from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.comment import Comment
from app.models.article import Article
from app.schemas.comment import CommentCreate
from app.core.deps import get_current_user

router = APIRouter(prefix="/comments", tags=["Comments"])


# =========================
# SAFE HELPERS
# =========================
def clean_text(v: str):
    if v is None:
        return ""
    return v.strip()


# =========================
# GET comments for article
# =========================
@router.get("/{article_id}")
def get_comments(article_id: int, db: Session = Depends(get_db)):

    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    comments = (
        db.query(Comment)
        .filter(Comment.article_id == article_id)
        .order_by(Comment.id.desc())
        .all()
    )

    return [
        {
            "id": c.id,
            "content": c.content or "",
            "article_id": c.article_id,
            "user_id": c.user_id
        }
        for c in comments
    ]


# =========================
# CREATE comment
# =========================
@router.post("/")
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    content = clean_text(comment.content)

    # 🔥 VALIDATION
    if not content:
        raise HTTPException(status_code=400, detail="Comment cannot be empty")

    if len(content) < 2:
        raise HTTPException(status_code=400, detail="Comment too short")

    article = db.query(Article).filter(
        Article.id == comment.article_id
    ).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    new_comment = Comment(
        content=content,
        article_id=comment.article_id,
        user_id=user.id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return {
        "id": new_comment.id,
        "content": new_comment.content,
        "article_id": new_comment.article_id,
        "user_id": new_comment.user_id
    }


# =========================
# DELETE comment
# =========================
@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    user_role = getattr(getattr(user, "role", None), "name", None)

    if user_role != "admin" and comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="No permission")

    db.delete(comment)
    db.commit()

    return {
        "message": "deleted",
        "id": comment_id
    }