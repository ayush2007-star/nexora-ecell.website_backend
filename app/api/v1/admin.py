from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from pydantic import BaseModel

from app.core.responses import ApiResponse
from app.dependencies.auth import admin_required
from app.schemas.admin import RejectRegistrationSchema, CreateMentorSchema, UpdateMentorSchema
from app.services.admin_service import AdminService
from app.services.mentor_service import MentorService


router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)


class AdminMemberSchema(BaseModel):
    memberName: str
    memberEmail: str
    memberPhone: str
    role: Optional[str] = "Team Member"


class AdminDirectRegisterSchema(BaseModel):
    teamName: str
    eventName: Optional[str] = "Nexora Flagship Event"
    leaderName: str
    leaderEmail: str
    leaderPhone: str
    college: Optional[str] = "Nexora Campus"
    department: Optional[str] = "Computer Science / Engineering"
    year: Optional[str] = "3rd Year"
    rollNumber: Optional[str] = ""
    projectName: Optional[str] = None
    domain: Optional[str] = "Technology & Innovation"
    stage: Optional[str] = "Prototype / MVP"
    description: Optional[str] = "Directly registered via Admin Portal."
    eurekaTeamId: Optional[str] = "DIR-ADMIN"
    referralCodeUsed: Optional[str] = ""
    pitchDeckUrl: Optional[str] = ""
    members: Optional[List[AdminMemberSchema]] = []


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


# -------------------------------------------------------------
# TEAM MEMBER MANAGEMENT BY ADMIN
# -------------------------------------------------------------

@router.post("/registration/{team_id}/members")
async def add_member(
    team_id: str,
    payload: AdminMemberSchema,
    user=Depends(admin_required),
):
    """
    Admin: Add a team member to a registration.
    """
    result = await AdminService.add_team_member(
        team_id=team_id,
        member_data=payload.model_dump(),
        admin_user=user,
    )

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return ApiResponse.success(
        message=result["message"],
        data=result.get("data"),
    )


@router.put("/registration/{team_id}/members/{member_id}")
async def update_member(
    team_id: str,
    member_id: str,
    payload: AdminMemberSchema,
    user=Depends(admin_required),
):
    """
    Admin: Update a team member's details.
    """
    result = await AdminService.update_team_member(
        team_id=team_id,
        member_id=member_id,
        member_data=payload.model_dump(),
        admin_user=user,
    )

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return ApiResponse.success(
        message=result["message"],
        data=result.get("data"),
    )


@router.delete("/registration/{team_id}/members/{member_id}")
async def delete_member(
    team_id: str,
    member_id: str,
    user=Depends(admin_required),
):
    """
    Admin: Remove a team member.
    """
    result = await AdminService.delete_team_member(
        team_id=team_id,
        member_id=member_id,
        admin_user=user,
    )

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return ApiResponse.success(
        message=result["message"],
        data=None,
    )


# -------------------------------------------------------------
# DIRECT REGISTRATION BY ADMIN FOR EVENT
# -------------------------------------------------------------

@router.post("/events/{event_id}/direct-register")
async def direct_register(
    event_id: str,
    payload: AdminDirectRegisterSchema,
    user=Depends(admin_required),
):
    """
    Admin: Directly add/register a team with leader and members for an event.
    """
    result = await AdminService.direct_register_team(
        event_id=event_id,
        payload=payload.model_dump(),
        admin_user=user,
    )

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return ApiResponse.success(
        message=result["message"],
        data=result.get("data"),
        status_code=status.HTTP_201_CREATED,
    )


# -------------------------------------------------------------
# MENTOR & JUDGE MANAGEMENT BY ADMIN
# -------------------------------------------------------------

@router.get("/mentors")
async def get_all_mentors(
    user=Depends(admin_required),
):
    """
    Admin: Fetch all registered Mentors / Judges with evaluation metrics.
    """
    result = await MentorService.get_all_mentors()
    return ApiResponse.success(
        message=result["message"],
        data=result["data"],
    )


@router.post("/mentors", status_code=status.HTTP_201_CREATED)
async def create_mentor(
    payload: CreateMentorSchema,
    user=Depends(admin_required),
):
    """
    Admin: Register a new Mentor / Judge with email, password, and specialization.
    """
    result = await MentorService.create_mentor(
        data=payload.model_dump(),
        admin_user=user,
    )

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return ApiResponse.success(
        message=result["message"],
        data=result["data"],
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/mentors/{user_id}")
async def update_mentor(
    user_id: str,
    payload: UpdateMentorSchema,
    user=Depends(admin_required),
):
    """
    Admin: Update Mentor / Judge details, email ID, or password.
    """
    result = await MentorService.update_mentor(
        user_id=user_id,
        data={k: v for k, v in payload.model_dump().items() if v is not None},
        admin_user=user,
    )

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return ApiResponse.success(
        message=result["message"],
        data=result["data"],
    )


@router.delete("/mentors/{user_id}")
async def delete_mentor(
    user_id: str,
    user=Depends(admin_required),
):
    """
    Admin: Delete or remove a Mentor / Judge account.
    """
    result = await MentorService.delete_mentor(
        user_id=user_id,
        admin_user=user,
    )

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return ApiResponse.success(
        message=result["message"],
        data=None,
    )