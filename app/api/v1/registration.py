from fastapi import APIRouter, status

from app.core.responses import ApiResponse
from app.schemas.registration import RegistrationSchema
from app.services.registration_service import RegistrationService


router = APIRouter(
    prefix="/api/v1/registration",
    tags=["Registration"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegistrationSchema,
):
    result = await RegistrationService.register(
        payload.model_dump()
    )

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return ApiResponse.success(
        message=result["message"],
        data={
            "userId": result["userId"],
            "teamId": result["teamId"],
            "status": result["status"],
        },
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/track/{identifier}",
    status_code=status.HTTP_200_OK,
)
async def track_registration(
    identifier: str,
):
    """
    Public registration status tracking by Team ID or Email.
    """
    result = await RegistrationService.track(identifier)

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return ApiResponse.success(
        message=result["message"],
        data=result["data"],
    )