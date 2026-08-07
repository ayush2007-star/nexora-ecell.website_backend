from fastapi import APIRouter

from app.services.certificate_service import CertificateService

from app.core.responses import ApiResponse

router = APIRouter(
    prefix="/api/v1/certificate",
    tags=["Certificate"]
)


@router.post("/generate/{team_id}")
async def generate(team_id: str):

    data = await CertificateService.generate(team_id)

    return ApiResponse.success(
        message="Certificate generated successfully.",
        data=data
    )


@router.get("/verify/{certificate_id}")
async def verify(certificate_id: str):

    data = await CertificateService.verify(certificate_id)

    if not data:

        return ApiResponse.error(
            message="Certificate not found."
        )

    return ApiResponse.success(
        message="Certificate verified.",
        data=data
    )