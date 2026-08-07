from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token


class AuthService:

    @staticmethod
    async def set_password(data):

        user = await UserRepository.find_by_email(data["email"])

        if not user:
            return {
                "success": False,
                "message": "User not found."
            }

        if not user["isApproved"]:
            return {
                "success": False,
                "message": "Your registration is not approved yet."
            }

        password = hash_password(data["password"])

        await UserRepository.update(
            user["userId"],
            {
                "password": password
            }
        )

        return {
            "success": True,
            "message": "Password created successfully."
        }

    @staticmethod
    async def login(data):

        user = await UserRepository.find_by_email(data["email"])

        if not user:
            return {
                "success": False,
                "message": "Invalid email or password."
            }

        if not user["password"]:
            return {
                "success": False,
                "message": "Please create password first."
            }

        if not verify_password(
            data["password"],
            user["password"]
        ):
            return {
                "success": False,
                "message": "Invalid email or password."
            }

        token = create_access_token(
            {
                "userId": user["userId"],
                "role": user["role"]
            }
        )

        return {
            "success": True,
            "message": "Login successful.",
            "token": token,
            "user": {
                "userId": user["userId"],
                "fullName": user["fullName"],
                "role": user["role"]
            }
        }