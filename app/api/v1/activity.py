from fastapi import APIRouter
from app.repositories.activity_repository import ActivityRepository
from app.core.responses import ApiResponse

router = APIRouter(
    prefix="/api/v1/activity",
    tags=["Activity Logs"]
)


@router.get("/")
async def get_activity():

    data = await ActivityRepository.get_all()

    return ApiResponse.success(
        message="Activity logs fetched successfully.",
        data=data
    )