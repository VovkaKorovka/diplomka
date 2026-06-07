from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.comment import Comment
from app.models.article import Article
from app.schemas.comment import CommentCreate
from app.core.deps import get_current_user

router = APIRouter(prefix="/comments", tags=["Comments"])


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
def validate_comment(content: str):
    content = clean(content)

    if not content:
        error(400, "Comment cannot be empty", "content")

    if len(content) < 2:
        error(400, "Comment too short (min 2 chars)", "content")

    if len(content) > 2000:
        error(400, "Comment too long (max 2000 chars)", "content")

    return content


# =========================
# 📄 GET COMMENTS
# =========================
@router.get("/{article_id}")
def get_comments(article_id: int, db: Session = Depends(get_db)):

    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        error(404, "Article not found")

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
# ➕ CREATE COMMENT
# =========================
@router.post("/")
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    content = validate_comment(comment.content)

    article = db.query(Article).filter(
        Article.id == comment.article_id
    ).first()

    if not article:
        error(404, "Article not found")

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
# ❌ DELETE COMMENT
# =========================
@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        error(404, "Comment not found")

    user_role = getattr(getattr(user, "role", None), "name", None)

    if user_role != "admin" and comment.user_id != user.id:
        error(403, "You don't have permission to delete this comment")

    db.delete(comment)
    db.commit()

    return {
        "message": "deleted",
        "id": comment_id
    }