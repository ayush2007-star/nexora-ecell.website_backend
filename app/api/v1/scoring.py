from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException

from app.core.responses import ApiResponse
from app.dependencies.auth import admin_required, mentor_or_admin_required, get_current_user
from app.schemas.scoring import MentorSubmitScoreSchema, AdminUpdateScoreSchema
from app.services.scoring_service import ScoringService

router = APIRouter(
    prefix="/api/v1/scoring",
    tags=["Mentor & Judge Scoring"],
)


@router.get("/mentor/startups")
async def get_mentor_startups(
    user=Depends(mentor_or_admin_required),
):
    """
    Mentor: Get list of all startups/teams with evaluation status and saved scores for the logged-in mentor.
    """
    mentor_id = user.get("userId")
    result = await ScoringService.get_startups_for_mentor(mentor_id=mentor_id)

    return ApiResponse.success(
        message=result["message"],
        data={
            "startups": result["data"],
            "metrics": result["metrics"],
            "currentMentor": {
                "userId": user.get("userId"),
                "fullName": user.get("fullName"),
                "mentorIndex": user.get("mentorIndex", 1),
            },
        },
    )


@router.post("/mentor/submit")
async def submit_mentor_score(
    payload: MentorSubmitScoreSchema,
    user=Depends(mentor_or_admin_required),
):
    """
    Mentor: Submit or update score for a specific startup across the 6 criteria (0-5 each).
    """
    result = await ScoringService.submit_score(
        team_id=payload.teamId,
        mentor_user=user,
        scores_dict=payload.scores.model_dump(),
        feedback=payload.feedback or "",
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


@router.get("/admin/results")
async def get_admin_results(
    user=Depends(admin_required),
):
    """
    Admin: Get combined 4-mentor leaderboard, rankings, and totals for all startups.
    """
    result = await ScoringService.get_all_results_leaderboard()

    return ApiResponse.success(
        message=result["message"],
        data={
            "leaderboard": result["data"],
            "metrics": result["metrics"],
        },
    )


@router.get("/admin/details/{team_id}")
async def get_admin_startup_details(
    team_id: str,
    user=Depends(admin_required),
):
    """
    Admin: Get full 6-criteria breakdown of all mentor scores for a single startup.
    """
    result = await ScoringService.get_startup_detailed_scores(team_id=team_id)

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return ApiResponse.success(
        message=result["message"],
        data=result.get("data"),
    )


@router.put("/admin/score/{team_id}/{mentor_id}")
async def admin_override_score(
    team_id: str,
    mentor_id: str,
    payload: MentorSubmitScoreSchema,
    user=Depends(admin_required),
):
    """
    Admin: Override/correct mentor score if needed.
    """
    # Extract mentor index from mentor_id
    m_idx = 1
    if "2" in mentor_id:
        m_idx = 2
    elif "3" in mentor_id:
        m_idx = 3
    elif "4" in mentor_id:
        m_idx = 4

    mentor_user_payload = {
        "userId": mentor_id,
        "fullName": f"Mentor {m_idx}",
        "mentorIndex": m_idx,
    }

    result = await ScoringService.submit_score(
        team_id=team_id,
        mentor_user=mentor_user_payload,
        scores_dict=payload.scores.model_dump(),
        feedback=payload.feedback or "",
    )

    if not result["success"]:
        return ApiResponse.error(
            message=result["message"],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return ApiResponse.success(
        message="Score updated by Admin successfully.",
        data=result.get("data"),
    )
