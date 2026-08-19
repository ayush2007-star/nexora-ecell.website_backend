from datetime import datetime, timezone
import logging

from app.email.email_service import EmailService
from app.repositories.activity_repository import ActivityRepository
from app.repositories.admin_repository import AdminRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository


logger = logging.getLogger(__name__)


class AdminService:
    """
    Business logic for administrator operations.
    """

    @staticmethod
    async def dashboard():
        data = await AdminRepository.dashboard_stats()

        return {
            "success": True,
            "message": "Dashboard loaded successfully.",
            "data": data,
        }

    @staticmethod
    async def registrations():
        data = await AdminRepository.registration_list()

        return {
            "success": True,
            "message": "Registrations fetched successfully.",
            "data": data,
        }

    @staticmethod
    async def get_all_registrations(
        page: int,
        limit: int,
        search: str,
        status: str,
    ):
        result = await AdminRepository.get_all_registrations(
            page=page,
            limit=limit,
            search=search,
            status=status,
        )

        return {
            "success": True,
            "message": "Registrations fetched successfully.",
            "data": result["data"],
            "pagination": result["pagination"],
        }

    @staticmethod
    async def registration(team_id: str):
        data = await AdminRepository.registration_details(team_id)

        if data is None:
            return {
                "success": False,
                "message": "Team not found.",
            }

        return {
            "success": True,
            "message": "Registration details fetched successfully.",
            "data": data,
        }

    @staticmethod
    async def approve(
        team_id: str,
        admin_user: dict,
    ):
        team_data = await AdminRepository.registration_details(team_id)

        if not team_data:
            return {
                "success": False,
                "message": "Team not found.",
            }

        team = team_data["team"]
        leader = team_data.get("leader")

        if not leader:
            return {
                "success": False,
                "message": "Team leader not found.",
            }

        current_status = str(
            team.get("status", "")
        ).strip().lower()

        if current_status == "approved":
            return {
                "success": False,
                "message": "This registration is already approved.",
            }

        now = datetime.now(timezone.utc)

        await AdminRepository.approve(team_id)

        await UserRepository.update(
            team["leaderId"],
            {
                "status": "Approved",
                "isApproved": True,
                "approvedAt": now,
                "approvedBy": admin_user.get("userId"),
            },
        )

        await ActivityRepository.create(
            {
                "userId": admin_user.get("userId"),
                "role": "admin",
                "action": "APPROVED",
                "module": "Registration",
                "teamId": team_id,
                "description": "Team registration approved.",
                "createdAt": now,
            }
        )

        await NotificationRepository.create(
            {
                "userId": team["leaderId"],
                "title": "Registration Approved",
                "message": (
                    "Congratulations! Your Nexora registration "
                    "has been approved."
                ),
                "type": "success",
                "isRead": False,
                "createdAt": now,
            }
        )

        # Email should not undo a successful admin action.
        try:
            await EmailService.send_email(
                to=leader["email"],
                subject="Registration Approved - Nexora",
                body=(
                    "Congratulations!\n\n"
                    "Your Nexora registration has been approved.\n"
                    "You can now create your password and login "
                    "to the portal.\n\n"
                    "Regards,\n"
                    "Team Nexora"
                ),
            )
        except Exception:
            logger.exception(
                "Approval email could not be sent for team %s",
                team_id,
            )

        return {
            "success": True,
            "message": "Registration approved successfully.",
            "data": {
                "teamId": team_id,
                "status": "Approved",
            },
        }

    @staticmethod
    async def reject(
        team_id: str,
        remarks: str,
        admin_user: dict,
    ):
        team_data = await AdminRepository.registration_details(team_id)

        if not team_data:
            return {
                "success": False,
                "message": "Team not found.",
            }

        team = team_data["team"]
        leader = team_data.get("leader")

        if not leader:
            return {
                "success": False,
                "message": "Team leader not found.",
            }

        current_status = str(
            team.get("status", "")
        ).strip().lower()

        if current_status == "rejected":
            return {
                "success": False,
                "message": "This registration is already rejected.",
            }

        cleaned_remarks = remarks.strip()

        if not cleaned_remarks:
            return {
                "success": False,
                "message": "Rejection remarks are required.",
            }

        now = datetime.now(timezone.utc)

        await AdminRepository.reject(
            team_id,
            cleaned_remarks,
        )

        await UserRepository.update(
            team["leaderId"],
            {
                "status": "Rejected",
                "isApproved": False,
                "rejectedAt": now,
                "rejectedBy": admin_user.get("userId"),
            },
        )

        await ActivityRepository.create(
            {
                "userId": admin_user.get("userId"),
                "role": "admin",
                "action": "REJECTED",
                "module": "Registration",
                "teamId": team_id,
                "description": (
                    f"Team registration rejected. "
                    f"Remarks: {cleaned_remarks}"
                ),
                "createdAt": now,
            }
        )

        await NotificationRepository.create(
            {
                "userId": team["leaderId"],
                "title": "Registration Rejected",
                "message": (
                    "Your Nexora registration has been rejected. "
                    "Please check the remarks and contact the E-Cell team."
                ),
                "type": "error",
                "isRead": False,
                "createdAt": now,
            }
        )

        try:
            await EmailService.send_email(
                to=leader["email"],
                subject="Registration Update - Nexora",
                body=(
                    "Your Nexora registration has been rejected.\n\n"
                    f"Remarks:\n{cleaned_remarks}\n\n"
                    "Please contact the E-Cell team for further information.\n\n"
                    "Regards,\n"
                    "Team Nexora"
                ),
            )
        except Exception:
            logger.exception(
                "Rejection email could not be sent for team %s",
                team_id,
            )

        return {
            "success": True,
            "message": "Registration rejected successfully.",
            "data": {
                "teamId": team_id,
                "status": "Rejected",
                "remarks": cleaned_remarks,
            },
        }