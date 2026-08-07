from app.database.collections import get_collections


class MemberRepository:

    @staticmethod
    async def create(document: dict, session=None):
        members = get_collections()["members"]
        return await members.insert_one(document)

    @staticmethod
    async def create_many(documents: list, session=None):
        members = get_collections()["members"]
        return await members.insert_many(documents)

    @staticmethod
    async def find_by_team(team_id: str, session=None):
        members = get_collections()["members"]
        return await members.find(
            {"teamId": team_id}
        ).to_list(length=None)
