from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from pydantic import BaseModel, Field

from app.core.responses import ApiResponse
from app.dependencies.auth import admin_required
from app.services.attendance_service import AttendanceService

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Attendance & Food"],
)


class UpdateAttendanceSchema(BaseModel):
    attendanceStatus: str = Field(..., pattern=r"^(?i)(present|absent)$")


class UpdateFoodSchema(BaseModel):
    foodStatus: str = Field(..., pattern=r"^(?i)(food done|done|food pending|pending)$")


@router.get("/attendance")
async def get_attendance(
    search: str = Query("", max_length=100),
    attendance: str = Query("", max_length=30),
    food: str = Query("", max_length=30),
    user=Depends(admin_required),
):
    """
    Get full attendance and food distribution list with counts and filters.
    """
    result = await AttendanceService.get_attendance_list(
        search=search,
        attendance=attendance,
        food=food,
    )

    return ApiResponse.success(
        message=result["message"],
        data={
            "records": result["data"],
            "counts": result["counts"],
        },
    )


@router.put("/attendance/{team_id}")
async def update_attendance(
    team_id: str,
    payload: UpdateAttendanceSchema,
    user=Depends(admin_required),
):
    """
    Mark participant/team as Present or Absent.
    """
    result = await AttendanceService.update_attendance(
        team_id=team_id,
        status=payload.attendanceStatus,
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


@router.put("/food/{team_id}")
async def update_food(
    team_id: str,
    payload: UpdateFoodSchema,
    user=Depends(admin_required),
):
    """
    Mark participant/team food status as Food Done or Food Pending.
    """
    result = await AttendanceService.update_food(
        team_id=team_id,
        status=payload.foodStatus,
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


@router.put("/attendance/{team_id}/member/{member_id}")
async def update_member_attendance(
    team_id: str,
    member_id: str,
    payload: UpdateAttendanceSchema,
    user=Depends(admin_required),
):
    """
    Mark individual team member as Present or Absent.
    """
    result = await AttendanceService.update_member_attendance(
        team_id=team_id,
        member_id=member_id,
        status=payload.attendanceStatus,
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


@router.put("/food/{team_id}/member/{member_id}")
async def update_member_food(
    team_id: str,
    member_id: str,
    payload: UpdateFoodSchema,
    user=Depends(admin_required),
):
    """
    Mark individual team member food status as Food Done or Food Pending.
    """
    result = await AttendanceService.update_member_food(
        team_id=team_id,
        member_id=member_id,
        status=payload.foodStatus,
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
