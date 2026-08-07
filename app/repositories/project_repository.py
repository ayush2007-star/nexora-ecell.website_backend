from app.database.collections import get_collections


class ProjectRepository:

    @staticmethod
    async def create(document: dict, session=None):
        projects = get_collections()["projects"]
        return await projects.insert_one(document)

    @staticmethod
    async def find_by_project_id(project_id: str, session=None):
        projects = get_collections()["projects"]
        return await projects.find_one(
            {"projectId": project_id}
        )

    @staticmethod
    async def update(project_id: str, data: dict, session=None):
        projects = get_collections()["projects"]
        return await projects.update_one(
            {"projectId": project_id},
            {"$set": data}
        )
