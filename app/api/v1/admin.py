from fastapi import APIRouter, Depends, Query, status

from app.core.responses import ApiResponse
from app.dependencies.auth import admin_required
from app.schemas.admin import RejectRegistrationSchema
from app.services.admin_service import AdminService


router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)


@router.get("/dashboard")
async def dashboard(
    user=Depends(admin_required),
):
    result = await AdminService.dashboard()

    return ApiResponse.success(
        message=result["message"],
        data=result["data"],
    )


@router.get("/registrations")
async def registrations(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query("", max_length=100),
    status_filter: str = Query(
        "",
        alias="status",
        max_length=30,
    ),
    user=Depends(admin_required),
):
    result = await AdminService.get_all_registrations(
        page=page,
        limit=limit,
        search=search.strip(),
        status=status_filter.strip(),
    )

    return ApiResponse.success(
        message=result["message"],
        data={
            "registrations": result["data"],
            "pagination": result["pagination"],
        },
    )


@router.get("/registration/{team_id}")
async def registration(
    team_id: str,
    user=Depends(admin_required),
):
    result = await AdminService.registration(team_id)

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return ApiResponse.success(
        message=result["message"],
        data=result["data"],
    )


@router.put("/approve/{team_id}")
async def approve(
    team_id: str,
    user=Depends(admin_required),
):
    result = await AdminService.approve(
        team_id=team_id,
        admin_user=user,
    )

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return ApiResponse.success(
        message=result["message"],
        data=result.get("data"),
    )


@router.put("/reject/{team_id}")
async def reject(
    team_id: str,
    payload: RejectRegistrationSchema,
    user=Depends(admin_required),
):
    result = await AdminService.reject(
        team_id=team_id,
        remarks=payload.remarks,
        admin_user=user,
    )

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return ApiResponse.success(
        message=result["message"],
        data=result.get("data"),
    )