from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.responses import ApiResponse
from app.dependencies.auth import admin_required
from app.services.certificate_service import CertificateService


router = APIRouter(
    prefix="/api/v1/certificate",
    tags=["Certificate"],
)


class CertificateDesignSchema(BaseModel):
    theme: Optional[str] = "gold"
    title: Optional[str] = "Certificate of Excellence"
    eventTitle: Optional[str] = None
    issuerName: Optional[str] = "Prof. A. K. Sharma"
    issuerTitle: Optional[str] = "Convener & Head of Incubation"
    customMessage: Optional[str] = None


@router.post("/generate/{team_id}")
async def generate(
    team_id: str,
    payload: Optional[CertificateDesignSchema] = None,
    admin=Depends(admin_required),
):
    """
    Generate certificate for a single team with customizable design options.
    """
    options = payload.model_dump() if payload else {}
    try:
        data = await CertificateService.generate(team_id, options)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return ApiResponse.success(
        message="Certificate generated successfully.",
        data=data,
    )


@router.post("/bulk-generate/{event_id}")
async def bulk_generate(
    event_id: str,
    payload: Optional[CertificateDesignSchema] = None,
    admin=Depends(admin_required),
):
    """
    Generate certificates for ALL approved teams of a specific event (or ALL events).
    """
    options = payload.model_dump() if payload else {}
    data = await CertificateService.bulk_generate(event_id, options)
    return ApiResponse.success(
        message=f"Generated {data['count']} certificates successfully.",
        data=data,
    )


@router.get("/verify/{certificate_id}")
async def verify(
    certificate_id: str,
):
    """
    Public certificate verification endpoint.
    No login required.
    """
    data = await CertificateService.verify(certificate_id)

    if not data:
        return ApiResponse.error(
            message="Certificate not found.",
            status_code=404,
        )

    return ApiResponse.success(
        message="Certificate verified successfully.",
        data=data,
    )


@router.get("/team/{team_id}")
async def get_by_team(
    team_id: str,
):
    """
    Get certificate for a specific team if generated.
    """
    data = await CertificateService.get_by_team(team_id)

    if not data:
        return ApiResponse.error(
            message="No certificate found for this team.",
            status_code=404,
        )

    return ApiResponse.success(
        message="Certificate fetched successfully.",
        data=data,
    )