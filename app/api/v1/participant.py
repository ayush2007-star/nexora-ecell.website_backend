from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, HttpUrl

from app.core.responses import ApiResponse
from app.dependencies.auth import get_current_user
from app.database.collections import get_collections
from app.repositories.activity_repository import ActivityRepository

router = APIRouter(
    prefix="/api/v1/participant",
    tags=["Participant Portal"],
)


class UpdatePitchDeckSchema(BaseModel):
    pitchDeckUrl: str


@router.get("/profile")
async def get_participant_profile(
    user=Depends(get_current_user),
):
    """
    Participant / Student: Fetch full team profile, attendance status, meal pass, and certificates.
    """
    user_id = user.get("userId")
    collections = get_collections()
    users_col = collections["users"]
    teams_col = collections["teams"]
    projects_col = collections["projects"]
    members_col = collections["members"]
    certs_col = collections["certificates"]

    # Find user
    user_doc = await users_col.find_one({"userId": user_id}, {"_id": 0, "password": 0})
    if not user_doc:
        # Check by email if userId was different
        email = user.get("email")
        if email:
            user_doc = await users_col.find_one({"email": email.lower()}, {"_id": 0, "password": 0})

    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant user profile not found.",
        )

    # Find team
    team_doc = await teams_col.find_one({"leaderId": user_doc["userId"]}, {"_id": 0})
    if not team_doc:
        # Check if user is a member of any team
        member_doc = await members_col.find_one({"memberEmail": user_doc["email"].lower()}, {"_id": 0})
        if member_doc:
            team_doc = await teams_col.find_one({"teamId": member_doc.get("teamId")}, {"_id": 0})

    team_id = team_doc.get("teamId") if team_doc else None

    project_doc = None
    cert_doc = None
    members_list = []

    if team_id:
        project_doc = await projects_col.find_one({"teamId": team_id}, {"_id": 0})
        cert_doc = await certs_col.find_one({"teamId": team_id}, {"_id": 0})
        members_list = await members_col.find({"teamId": team_id}, {"_id": 0}).to_list(length=None)

    # Generate Digital Meal Token
    eureka_id = project_doc.get("eurekaTeamId") if project_doc else team_id or user_id
    meal_token = f"NEXORA-MEAL-{eureka_id}"

    return ApiResponse.success(
        message="Participant profile loaded successfully.",
        data={
            "user": user_doc,
            "team": team_doc or {
                "teamId": "NOT_ASSIGNED",
                "teamName": "Individual Participant",
                "attendanceStatus": "Absent",
                "foodStatus": "Food Pending",
            },
            "project": project_doc or {
                "projectName": "Innovation Project",
                "eurekaTeamId": eureka_id,
                "domain": "Technology & Entrepreneurship",
                "stage": "MVP",
                "pitchDeckUrl": "",
            },
            "members": members_list,
            "certificate": cert_doc,
            "mealPass": {
                "token": meal_token,
                "foodStatus": team_doc.get("foodStatus", "Food Pending") if team_doc else "Food Pending",
                "attendanceStatus": team_doc.get("attendanceStatus", "Absent") if team_doc else "Absent",
                "updatedAt": team_doc.get("foodUpdatedAt") if team_doc else None,
            },
        },
    )


@router.put("/pitchdeck")
async def update_pitch_deck(
    payload: UpdatePitchDeckSchema,
    user=Depends(get_current_user),
):
    """
    Participant: Update team pitch deck URL.
    """
    user_id = user.get("userId")
    collections = get_collections()
    teams_col = collections["teams"]
    projects_col = collections["projects"]

    team_doc = await teams_col.find_one({"leaderId": user_id})
    if not team_doc:
        return ApiResponse.error(
            message="No team found for this user account.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    team_id = team_doc.get("teamId")
    now = datetime.now(timezone.utc)

    await projects_col.update_one(
        {"teamId": team_id},
        {"$set": {"pitchDeckUrl": payload.pitchDeckUrl.strip(), "updatedAt": now}},
    )

    return ApiResponse.success(
        message="Pitch deck URL updated successfully.",
        data={"teamId": team_id, "pitchDeckUrl": payload.pitchDeckUrl.strip()},
    )


@router.post("/claim-food")
async def claim_food_pass(
    user=Depends(get_current_user),
):
    """
    Participant: Generate active meal coupon pass for event canteen / food counter.
    """
    user_id = user.get("userId")
    collections = get_collections()
    teams_col = collections["teams"]
    projects_col = collections["projects"]

    team_doc = await teams_col.find_one({"leaderId": user_id})
    if not team_doc:
        return ApiResponse.error(
            message="No team found for this user account.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    team_id = team_doc.get("teamId")
    project = await projects_col.find_one({"teamId": team_id})
    eureka_id = project.get("eurekaTeamId") if project else team_id

    return ApiResponse.success(
        message="Digital meal token verified and active.",
        data={
            "token": f"MEAL-{eureka_id}",
            "teamName": team_doc.get("teamName"),
            "eurekaTeamId": eureka_id,
            "status": team_doc.get("foodStatus", "Food Pending"),
            "attendanceStatus": team_doc.get("attendanceStatus", "Absent"),
        },
    )
