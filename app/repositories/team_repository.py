from app.database.collections import get_collections


class TeamRepository:

    @staticmethod
    async def create(document: dict, session=None):
        teams = get_collections()["teams"]
        return await teams.insert_one(document)

    @staticmethod
    async def find(team_id: str, session=None):
        teams = get_collections()["teams"]
        return await teams.find_one(
            {"teamId": team_id}
        )

    @staticmethod
    async def update(team_id: str, data: dict, session=None):
        teams = get_collections()["teams"]
        return await teams.update_one(
            {"teamId": team_id},
            {"$set": data}
        )
