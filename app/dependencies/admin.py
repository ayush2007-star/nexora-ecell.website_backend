from fastapi import Depends, HTTPException, status
from app.dependencies.auth import get_current_user


def require_admin(user: str = Depends(get_current_user)):
    if user != "admin-token":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
