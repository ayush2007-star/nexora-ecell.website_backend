from fastapi import APIRouter, Query
from app.dependencies.auth import admin_required
from fastapi import Depends
from app.services.admin_service import AdminService
from app.schemas.admin import (
    RejectRegistrationSchema,
)

from app.core.responses import ApiResponse

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"]
)


@router.get("/dashboard")
async def dashboard(

    user=Depends(admin_required)

):

    result = await AdminService.dashboard()

    return ApiResponse.success(
        message=result["message"],
        data=result["data"]
    )


@router.get("/registrations")
async def registrations(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = "",
    status: str = ""
):

    result = await AdminService.get_all_registrations(
        page,
        limit,
        search,
        status
    )

    return ApiResponse.success(
        message=result["message"],
        data={
            "registrations": result["data"],
            "pagination": result["pagination"]
        }
    )


@router.get("/registration/{team_id}")
async def registration(team_id: str):

    result = await AdminService.registration(team_id)

    if result["success"]:
        return ApiResponse.success(
            message=result["message"],
            data=result["data"]
        )

    return ApiResponse.error(
        message=result["message"],
        status_code=404
    )


@router.put("/approve/{team_id}")
async def approve(team_id: str):

    result = await AdminService.approve(team_id)

    return ApiResponse.success(
        message=result["message"]
    )


@router.put("/reject/{team_id}")
async def reject(
    team_id: str,
    payload: RejectRegistrationSchema
):

    result = await AdminService.reject(
        team_id,
        payload.remarks
    )

    return ApiResponse.success(
        message=result["message"]
    )