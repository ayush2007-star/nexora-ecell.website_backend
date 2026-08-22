from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.utils.jwt import verify_token


security = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:

    token = credentials.credentials

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("userId")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def admin_required(
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:

    role = str(user.get("role", "")).strip().lower()

    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return user


async def mentor_or_admin_required(
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:

    role = str(user.get("role", "")).strip().lower()

    if role not in ["admin", "mentor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mentor or Admin access required.",
        )

    return user


async def mentor_required(
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:

    role = str(user.get("role", "")).strip().lower()

    if role not in ["mentor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mentor access required.",
        )

    return user


async def management_required(
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:

    role = str(user.get("role", "")).strip().lower()

    if role not in ["management", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Management access required.",
        )

    return user