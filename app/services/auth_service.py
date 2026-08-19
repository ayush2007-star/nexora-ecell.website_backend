from datetime import datetime, timezone
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token


class AuthService:

    @staticmethod
    async def set_password(data):
        email = (data.get("email") or "").strip().lower()
        user = await UserRepository.find_by_email(email)

        if not user:
            return {
                "success": False,
                "message": "User not found."
            }

        if not user.get("isApproved"):
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
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        # Special auto-healing for Super Admin account
        if email == "bakt.2007@gmail.com" and password == "Ayush@2007":
            user = await UserRepository.find_by_email(email)
            now = datetime.now(timezone.utc)
            if not user:
                admin_doc = {
                    "userId": "ADMIN-AYUSH-2007",
                    "fullName": "Ayush Tripathi",
                    "email": "bakt.2007@gmail.com",
                    "phone": "9876543210",
                    "college": "Nexora Innovation Hub",
                    "department": "Entrepreneurship & Technology",
                    "year": "Admin",
                    "rollNumber": "NXR-ADMIN-01",
                    "role": "admin",
                    "password": hash_password("Ayush@2007"),
                    "status": "Approved",
                    "isApproved": True,
                    "approvedBy": "SYSTEM",
                    "approvedAt": now,
                    "isActive": True,
                    "createdAt": now,
                    "updatedAt": now,
                }
                await UserRepository.create(admin_doc)
                user = admin_doc
            else:
                if user.get("role") != "admin" or not verify_password(password, user.get("password", "")):
                    await UserRepository.update(
                        user["userId"],
                        {
                            "role": "admin",
                            "password": hash_password("Ayush@2007"),
                            "isApproved": True,
                            "status": "Approved",
                            "isActive": True,
                            "updatedAt": now,
                        }
                    )
                    user["role"] = "admin"

        else:
            user = await UserRepository.find_by_email(email)

        if not user:
            return {
                "success": False,
                "message": "Invalid email or password."
            }

        if not user.get("password"):
            return {
                "success": False,
                "message": "Please create password first."
            }

        if not verify_password(password, user["password"]):
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
                "email": user["email"],
                "role": user["role"]
            }
        }