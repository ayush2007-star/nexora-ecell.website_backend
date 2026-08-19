from datetime import datetime, timezone

from app.database.collections import get_collections


class NotificationRepository:
    """
    Repository for user notifications.
    """

    @staticmethod
    async def create(
        document: dict,
        session=None,
    ):
        notifications = get_collections()["notifications"]

        notification = {
            "userId": document["userId"],
            "title": document["title"],
            "message": document["message"],
            "type": document.get("type", "info"),
            "isRead": document.get("isRead", False),
            "createdAt": document.get(
                "createdAt",
                datetime.now(timezone.utc),
            ),
        }

        return await notifications.insert_one(
            notification,
            session=session,
        )

    @staticmethod
    async def get_by_user(
        user_id: str,
        session=None,
    ):
        notifications = get_collections()["notifications"]

        cursor = notifications.find(
            {"userId": user_id},
            session=session,
        ).sort("createdAt", -1)

        return await cursor.to_list(length=None)

    @staticmethod
    async def mark_as_read(
        user_id: str,
        notification_id,
        session=None,
    ):
        notifications = get_collections()["notifications"]

        return await notifications.update_one(
            {
                "_id": notification_id,
                "userId": user_id,
            },
            {
                "$set": {
                    "isRead": True,
                }
            },
            session=session,
        )