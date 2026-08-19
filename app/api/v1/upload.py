from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.responses import ApiResponse
from app.dependencies.auth import get_current_user
from app.services.upload_service import UploadService


router = APIRouter(
    prefix="/api/v1/upload",
    tags=["Upload"],
)


@router.post("/pitch-deck")
async def upload_pitch_deck(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    """
    Upload a pitch deck.

    Authentication required.
    Leaders and admins are allowed.
    """

    role = str(user.get("role", "")).upper()

    if role not in {"LEADER", "ADMIN"}:
        raise HTTPException(
            status_code=403,
            detail="Only team leaders or admins can upload pitch decks.",
        )

    try:
        result = await UploadService.save_pitch_deck(file)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return ApiResponse.success(
        message="Pitch deck uploaded successfully.",
        data={
            **result,
            "uploadedBy": user.get("userId"),
        },
        status_code=201,
    )