from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.utils.jwt import verify_token

security = HTTPBearer()


async def get_current_user(

    credentials: HTTPAuthorizationCredentials = Depends(security)

):

    token = credentials.credentials

    payload = verify_token(token)

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid or Expired Token"
        )

    return payload


async def admin_required(

    user=Depends(get_current_user)

):

    if user.get("role") != "ADMIN":

        raise HTTPException(
            status_code=403,
            detail="Admin access required."
        )

    return user
