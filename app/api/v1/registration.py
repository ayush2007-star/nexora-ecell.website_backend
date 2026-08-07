from fastapi import APIRouter

from app.core.responses import ApiResponse
from app.schemas.registration import RegistrationSchema
from app.services.registration_service import RegistrationService

router = APIRouter(
    prefix="/api/v1/registration",
    tags=["Registration"]
)


@router.post("/")
async def register(payload: RegistrationSchema):

    result = await RegistrationService.register(
        payload.model_dump()
    )

    if result["success"]:
        return ApiResponse.success(
            message=result["message"],
            data=result,
            status_code=201
        )

    return ApiResponse.error(
        message=result["message"],
        status_code=400
    )
