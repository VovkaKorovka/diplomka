from fastapi import Depends, HTTPException
from app.core.deps import get_current_user


def require_admin(user: User = Depends(get_current_user)):
    if not user.role or user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user