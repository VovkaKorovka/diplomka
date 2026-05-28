from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.article import Article
from app.schemas.article import ArticleCreate
from app.core.admin import get_current_admin
from app.core.deps import get_current_user, require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/articles")
def admin_get_articles(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    return db.query(Article).offset(offset).limit(limit).all()


@router.post("/articles")
def admin_create_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    new_article = Article(
        title=article.title,
        content=article.content,
        author_id=admin.id,
        culture_id=article.culture_id,  # 🔥 ОБОВʼЯЗКОВО
        is_album=bool(article.is_album),
        status="published"
    )

    db.add(new_article)
    db.commit()
    db.refresh(new_article)

    return new_article


@router.delete("/articles/{article_id}")
def admin_delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.delete(article)
    db.commit()

    return {"message": "Deleted"}