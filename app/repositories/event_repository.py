from datetime import datetime, timezone
from app.database.collections import get_collections


class EventRepository:

    @staticmethod
    def _collection():
        return get_collections()["events"]

    @staticmethod
    def _teams_collection():
        return get_collections()["teams"]

    @classmethod
    async def create(cls, doc: dict):
        col = cls._collection()
        if col is None:
            return doc
        await col.insert_one(doc)
        return doc

    @classmethod
    async def find_all(cls):
        col = cls._collection()
        if col is None:
            return []

        cursor = col.find().sort("createdAt", -1)
        events = []
        teams_col = cls._teams_collection()

        async for doc in cursor:
            doc["_id"] = str(doc.get("_id"))
            event_id = doc.get("eventId")

            # Attach live team count for each event
            if teams_col is not None and event_id:
                count = await teams_col.count_documents({"$or": [{"eventId": event_id}, {"event": event_id}]})
                doc["totalRegistrations"] = count
            else:
                doc["totalRegistrations"] = 0

            events.append(doc)

        return events

    @classmethod
    async def find_by_id(cls, event_id: str):
        col = cls._collection()
        if col is None:
            return None

        doc = await col.find_one({"eventId": event_id})
        if doc:
            doc["_id"] = str(doc.get("_id"))
            teams_col = cls._teams_collection()
            if teams_col is not None:
                doc["totalRegistrations"] = await teams_col.count_documents(
                    {"$or": [{"eventId": event_id}, {"event": event_id}]}
                )
            else:
                doc["totalRegistrations"] = 0
        return doc

    @classmethod
    async def find_public(cls):
        col = cls._collection()
        if col is None:
            return []

        cursor = col.find({"status": {"$in": ["Live", "Upcoming"]}}).sort("createdAt", -1)
        events = []
        async for doc in cursor:
            doc["_id"] = str(doc.get("_id"))
            events.append(doc)
        return events

    @classmethod
    async def update(cls, event_id: str, update_data: dict):
        col = cls._collection()
        if col is None:
            return None

        update_data["updatedAt"] = datetime.now(timezone.utc)
        await col.update_one({"eventId": event_id}, {"$set": update_data})
        return await cls.find_by_id(event_id)

    @classmethod
    async def delete(cls, event_id: str):
        col = cls._collection()
        if col is None:
            return False
        result = await col.delete_one({"eventId": event_id})
        return result.deleted_count > 0
