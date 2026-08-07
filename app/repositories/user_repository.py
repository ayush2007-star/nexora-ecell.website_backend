from app.database.collections import get_collections


class UserRepository:

    @staticmethod
    async def create(document: dict, session=None):
        users = get_collections()["users"]
        return await users.insert_one(document)

    @staticmethod
    async def find_by_email(email: str, session=None):
        users = get_collections()["users"]
        return await users.find_one(
            {"email": email.lower()}
        )

    @staticmethod
    async def find_by_user_id(user_id: str, session=None):
        users = get_collections()["users"]
        return await users.find_one(
            {"userId": user_id}
        )

    @staticmethod
    async def update(user_id: str, data: dict, session=None):
        users = get_collections()["users"]
        return await users.update_one(
            {"userId": user_id},
            {"$set": data}
        )

    @staticmethod
    async def delete(user_id: str, session=None):
        users = get_collections()["users"]
        return await users.delete_one(
            {"userId": user_id}
        )
