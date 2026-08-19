from datetime import datetime, timezone

from app.database.collections import get_collections


class ActivityRepository:
    """
    Repository for activity/audit logs.
    """

    @staticmethod
    async def create(
        document: dict,
        session=None,
    ):
        activity_logs = get_collections()["activity_logs"]

        activity = {
            "userId": document.get("userId"),
            "role": document.get("role"),
            "action": document["action"],
            "module": document.get("module"),
            "teamId": document.get("teamId"),
            "description": document["description"],
            "createdAt": document.get(
                "createdAt",
                datetime.now(timezone.utc),
            ),
        }

        return await activity_logs.insert_one(
            activity,
            session=session,
        )

    @staticmethod
    async def get_all(
        session=None,
    ):
        activity_logs = get_collections()["activity_logs"]

        cursor = activity_logs.find(
            {},
            {"_id": 0},
            session=session,
        ).sort("createdAt", -1)

        return await cursor.to_list(length=None)

    @staticmethod
    async def get_by_user(
        user_id: str,
        session=None,
    ):
        activity_logs = get_collections()["activity_logs"]

        cursor = activity_logs.find(
            {"userId": user_id},
            {"_id": 0},
            session=session,
        ).sort("createdAt", -1)

        return await cursor.to_list(length=None)