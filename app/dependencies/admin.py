from typing import Any
from fastapi import Depends
from app.dependencies.auth import admin_required


async def require_admin(user: dict[str, Any] = Depends(admin_required)) -> dict[str, Any]:
    return user
