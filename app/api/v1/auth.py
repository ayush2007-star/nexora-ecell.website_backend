from fastapi import APIRouter

from app.schemas.auth import (
    LoginSchema,
    SetPasswordSchema
)

from app.services.auth_service import AuthService
from app.core.responses import ApiResponse

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


@router.post("/set-password")
async def set_password(payload: SetPasswordSchema):

    result = await AuthService.set_password(
        payload.model_dump()
    )

    if result["success"]:
        return ApiResponse.success(
            result["message"],
            result
        )

    return ApiResponse.error(
        result["message"]
    )


@router.post("/login")
async def login(payload: LoginSchema):

    result = await AuthService.login(
        payload.model_dump()
    )

    if result["success"]:
        return ApiResponse.success(
            result["message"],
            result
        )

    return ApiResponse.error(
        result["message"]
    )