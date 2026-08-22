import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.repositories.mentor_repository import MentorRepository
from app.repositories.activity_repository import ActivityRepository

logger = logging.getLogger(__name__)


class MentorService:
    """
    Business logic for Admin managing Judge & Mentor registrations, credentials, and access.
    """

    @staticmethod
    async def get_all_mentors() -> Dict[str, Any]:
        mentors = await MentorRepository.get_all_mentors()
        return {
            "success": True,
            "message": "Mentors list retrieved successfully.",
            "data": mentors,
        }

    @staticmethod
    async def create_mentor(data: Dict[str, Any], admin_user: Dict[str, Any]) -> Dict[str, Any]:
        email = (data.get("email") or "").strip().lower()
        if not email or "@" not in email:
            return {
                "success": False,
                "message": "Please provide a valid email address.",
            }

        password = (data.get("password") or "").strip()
        if len(password) < 6:
            return {
                "success": False,
                "message": "Password must be at least 6 characters long.",
            }

        existing = await MentorRepository.find_mentor_by_email(email)
        if existing:
            return {
                "success": False,
                "message": f"A mentor with email '{email}' already exists.",
            }

        mentor = await MentorRepository.create_mentor(data)

        # Log Activity
        try:
            now = datetime.now(timezone.utc)
            await ActivityRepository.create({
                "userId": admin_user.get("userId", "ADMIN"),
                "role": "admin",
                "action": "MENTOR_REGISTERED",
                "module": "Mentor Management",
                "description": f"Registered new Judge/Mentor: {mentor.get('fullName')} ({email}).",
                "createdAt": now,
            })
        except Exception as e:
            logger.warning("Activity log error: %s", e)

        return {
            "success": True,
            "message": f"Mentor {mentor.get('fullName')} registered successfully! They can now log in with {email}.",
            "data": mentor,
        }

    @staticmethod
    async def update_mentor(
        user_id: str,
        data: Dict[str, Any],
        admin_user: Dict[str, Any],
    ) -> Dict[str, Any]:
        mentor = await MentorRepository.find_mentor_by_id(user_id)
        if not mentor:
            return {
                "success": False,
                "message": "Mentor not found.",
            }

        # Check email conflict if email changed
        new_email = (data.get("email") or "").strip().lower()
        if new_email and new_email != mentor.get("email"):
            existing = await MentorRepository.find_mentor_by_email(new_email)
            if existing and existing.get("userId") != user_id:
                return {
                    "success": False,
                    "message": f"Email '{new_email}' is already in use by another user.",
                }

        updated = await MentorRepository.update_mentor(user_id, data)

        # Log Activity
        try:
            now = datetime.now(timezone.utc)
            pwd_msg = " (password updated)" if data.get("password") else ""
            await ActivityRepository.create({
                "userId": admin_user.get("userId", "ADMIN"),
                "role": "admin",
                "action": "MENTOR_UPDATED",
                "module": "Mentor Management",
                "description": f"Updated credentials/details for mentor {user_id}{pwd_msg}.",
                "createdAt": now,
            })
        except Exception as e:
            logger.warning("Activity log error: %s", e)

        return {
            "success": True,
            "message": "Mentor details and credentials updated successfully.",
            "data": updated,
        }

    @staticmethod
    async def delete_mentor(user_id: str, admin_user: Dict[str, Any]) -> Dict[str, Any]:
        mentor = await MentorRepository.find_mentor_by_id(user_id)
        if not mentor:
            return {
                "success": False,
                "message": "Mentor not found.",
            }

        await MentorRepository.delete_mentor(user_id)

        try:
            now = datetime.now(timezone.utc)
            await ActivityRepository.create({
                "userId": admin_user.get("userId", "ADMIN"),
                "role": "admin",
                "action": "MENTOR_DELETED",
                "module": "Mentor Management",
                "description": f"Removed mentor account {user_id} ({mentor.get('fullName')}).",
                "createdAt": now,
            })
        except Exception as e:
            logger.warning("Activity log error: %s", e)

        return {
            "success": True,
            "message": f"Mentor {mentor.get('fullName')} deleted successfully.",
        }
