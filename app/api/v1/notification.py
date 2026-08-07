from fastapi import APIRouter
from app.database.collections import get_collections
from app.core.responses import ApiResponse

router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["Notifications"]
)


@router.get("/{user_id}")
async def get_notifications(user_id: str):

    collections = get_collections()

    notifications = collections["notifications"]

    data = await notifications.find(
        {"userId": user_id},
        {"_id": 0}
    ).sort("createdAt", -1).to_list(length=None)

    return ApiResponse.success(
        message="Notifications fetched successfully.",
        data=data
    )