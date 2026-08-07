from datetime import datetime
from app.database.collections import get_collections


class ActivityRepository:

    @staticmethod
    async def create(
        action: str,
        performed_by: str,
        team_id: str,
        description: str
    ):

        collections = get_collections()

        activity_logs = collections["activity_logs"]

        document = {
            "action": action,
            "performedBy": performed_by,
            "teamId": team_id,
            "description": description,
            "createdAt": datetime.utcnow()
        }

        return await activity_logs.insert_one(document)

    @staticmethod
    async def get_all():

        collections = get_collections()

        activity_logs = collections["activity_logs"]

        cursor = activity_logs.find(
            {},
            {"_id": 0}
        ).sort("createdAt", -1)

        return await cursor.to_list(length=None)