from typing import Any

from app.database.collections import get_collections


class UserRepository:
    """
    Repository layer for user-related MongoDB operations.
    """

    @staticmethod
    async def create(
        document: dict[str, Any],
        session=None,
    ):
        users = get_collections()["users"]

        return await users.insert_one(
            document,
            session=session,
        )

    @staticmethod
    async def find_by_email(
        email: str,
        session=None,
    ):
        users = get_collections()["users"]

        normalized_email = email.strip().lower()

        return await users.find_one(
            {"email": normalized_email},
            session=session,
        )

    @staticmethod
    async def find_by_user_id(
        user_id: str,
        session=None,
    ):
        users = get_collections()["users"]

        return await users.find_one(
            {"userId": user_id},
            session=session,
        )

    @staticmethod
    async def get_by_id(
        user_id: str,
        session=None,
    ):
        """
        Compatibility alias for services that use get_by_id().
        """

        return await UserRepository.find_by_user_id(
            user_id=user_id,
            session=session,
        )

    @staticmethod
    async def update(
        user_id: str,
        data: dict[str, Any],
        session=None,
    ):
        users = get_collections()["users"]

        return await users.update_one(
            {"userId": user_id},
            {"$set": data},
            session=session,
        )

    @staticmethod
    async def delete(
        user_id: str,
        session=None,
    ):
        users = get_collections()["users"]

        return await users.delete_one(
            {"userId": user_id},
            session=session,
        )