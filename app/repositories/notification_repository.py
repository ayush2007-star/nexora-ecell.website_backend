from datetime import datetime
from app.database.collections import get_collections


class NotificationRepository:

    @staticmethod
    async def create(user_id: str, title: str, message: str):

        collections = get_collections()

        notifications = collections["notifications"]

        document = {
            "userId": user_id,
            "title": title,
            "message": message,
            "isRead": False,
            "createdAt": datetime.utcnow()
        }

        return await notifications.insert_one(document)

    @staticmethod
    async def get_by_user(user_id: str):

        collections = get_collections()

        notifications = collections["notifications"]

        cursor = notifications.find(
            {"userId": user_id}
        ).sort("createdAt", -1)

        return await cursor.to_list(length=None)