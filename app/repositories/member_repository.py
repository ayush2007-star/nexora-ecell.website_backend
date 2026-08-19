from datetime import datetime, timezone
from app.database.collections import get_collections


class MemberRepository:

    @staticmethod
    async def create(document: dict, session=None):
        members = get_collections()["members"]
        if members is None:
            return None
        return await members.insert_one(document)

    @staticmethod
    async def create_many(documents: list, session=None):
        if not documents:
            return None
        members = get_collections()["members"]
        if members is None:
            return None
        return await members.insert_many(documents)

    @staticmethod
    async def find_by_team(team_id: str, session=None):
        members = get_collections()["members"]
        if members is None:
            return []
        return await members.find(
            {"teamId": team_id},
            {"_id": 0}
        ).to_list(length=None)

    @staticmethod
    async def find_by_id(team_id: str, member_id: str):
        members = get_collections()["members"]
        if members is None:
            return None
        return await members.find_one(
            {"$or": [{"memberId": member_id}, {"_id": member_id}], "teamId": team_id},
            {"_id": 0}
        )

    @staticmethod
    async def update_member(team_id: str, member_id: str, data: dict):
        members = get_collections()["members"]
        if members is None:
            return None
        data["updatedAt"] = datetime.now(timezone.utc)
        return await members.update_one(
            {"$or": [{"memberId": member_id}, {"_id": member_id}], "teamId": team_id},
            {"$set": data}
        )

    @staticmethod
    async def delete_member(team_id: str, member_id: str):
        members = get_collections()["members"]
        if members is None:
            return None
        return await members.delete_one(
            {"$or": [{"memberId": member_id}, {"_id": member_id}], "teamId": team_id}
        )
