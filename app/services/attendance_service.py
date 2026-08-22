import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.activity_repository import ActivityRepository

logger = logging.getLogger(__name__)


class AttendanceService:
    """
    Business logic for event attendance and food distribution management.
    """

    @staticmethod
    async def get_attendance_list(
        search: str = "",
        attendance: str = "",
        food: str = "",
    ) -> Dict[str, Any]:
        data = await AttendanceRepository.get_attendance_list(
            search=search,
            attendance_filter=attendance,
            food_filter=food,
        )
        return {
            "success": True,
            "message": "Attendance list fetched successfully.",
            "data": data["records"],
            "counts": data["counts"],
        }

    @staticmethod
    async def update_attendance(
        team_id: str,
        status: str,
        admin_user: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized = "Present" if status.strip().lower() == "present" else "Absent"
        admin_name = admin_user.get("fullName") if admin_user else "Admin"

        success = await AttendanceRepository.update_team_attendance(
            team_id=team_id,
            status=normalized,
            updated_by=admin_name,
        )

        if not success:
            return {
                "success": False,
                "message": "Team registration not found.",
            }

        # Log activity
        try:
            now = datetime.now(timezone.utc)
            await ActivityRepository.create({
                "userId": admin_user.get("userId") if admin_user else "ADMIN",
                "role": "admin",
                "action": "ATTENDANCE_UPDATE",
                "module": "Attendance",
                "teamId": team_id,
                "description": f"Marked team {team_id} as {normalized} by {admin_name}.",
                "createdAt": now,
            })
        except Exception as e:
            logger.warning("Activity log notice: %s", e)

        return {
            "success": True,
            "message": f"Attendance status updated to {normalized}.",
            "data": {
                "teamId": team_id,
                "attendanceStatus": normalized,
            },
        }

    @staticmethod
    async def update_food(
        team_id: str,
        status: str,
        admin_user: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized = "Food Done" if "done" in status.strip().lower() else "Food Pending"
        admin_name = admin_user.get("fullName") if admin_user else "Admin"

        success = await AttendanceRepository.update_team_food(
            team_id=team_id,
            status=normalized,
            updated_by=admin_name,
        )

        if not success:
            return {
                "success": False,
                "message": "Team registration not found.",
            }

        # Log activity
        try:
            now = datetime.now(timezone.utc)
            await ActivityRepository.create({
                "userId": admin_user.get("userId") if admin_user else "ADMIN",
                "role": "admin",
                "action": "FOOD_STATUS_UPDATE",
                "module": "Food Management",
                "teamId": team_id,
                "description": f"Marked food for team {team_id} as {normalized} by {admin_name}.",
                "createdAt": now,
            })
        except Exception as e:
            logger.warning("Activity log notice: %s", e)

        return {
            "success": True,
            "message": f"Food status updated to {normalized}.",
            "data": {
                "teamId": team_id,
                "foodStatus": normalized,
            },
        }

    @staticmethod
    async def update_member_attendance(
        team_id: str,
        member_id: str,
        status: str,
        admin_user: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized = "Present" if status.strip().lower() == "present" else "Absent"

        success = await AttendanceRepository.update_member_attendance(
            team_id=team_id,
            member_id=member_id,
            status=normalized,
        )

        if not success:
            return {
                "success": False,
                "message": "Team member not found.",
            }

        return {
            "success": True,
            "message": f"Member attendance updated to {normalized}.",
            "data": {
                "teamId": team_id,
                "memberId": member_id,
                "attendanceStatus": normalized,
            },
        }

    @staticmethod
    async def update_member_food(
        team_id: str,
        member_id: str,
        status: str,
        admin_user: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized = "Food Done" if "done" in status.strip().lower() else "Food Pending"

        success = await AttendanceRepository.update_member_food(
            team_id=team_id,
            member_id=member_id,
            status=normalized,
        )

        if not success:
            return {
                "success": False,
                "message": "Team member not found.",
            }

        return {
            "success": True,
            "message": f"Member food status updated to {normalized}.",
            "data": {
                "teamId": team_id,
                "memberId": member_id,
                "foodStatus": normalized,
            },
        }
