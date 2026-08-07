from datetime import datetime

from app.repositories.activity_repository import ActivityRepository
from app.repositories.admin_repository import AdminRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository


class AdminService:

    @staticmethod
    async def dashboard():

        data = await AdminRepository.dashboard()

        return {
            "success": True,
            "message": "Dashboard loaded successfully.",
            "data": data
        }

    @staticmethod
    async def registrations():

        data = await AdminRepository.registration_list()

        return {
            "success": True,
            "message": "Registrations fetched successfully.",
            "data": data
        }

    @staticmethod
    async def get_all_registrations(
        page: int,
        limit: int,
        search: str,
        status: str
    ):

        result = await AdminRepository.get_all_registrations(
            page,
            limit,
            search,
            status
        )

        return {
            "success": True,
            "message": "Registrations fetched successfully.",
            "data": result["data"],
            "pagination": result["pagination"]
        }

    @staticmethod
    async def registration(team_id: str):

        data = await AdminRepository.registration_details(team_id)

        if data is None:
            return {
                "success": False,
                "message": "Team not found."
            }

        return {
            "success": True,
            "message": "Registration details fetched.",
            "data": data
        }

    @staticmethod
    async def approve(team_id: str):

        team = await AdminRepository.registration_details(team_id)

        if not team:
            return {
                "success": False,
                "message": "Team not found."
            }

        await AdminRepository.approve(team_id)
        from app.email.email_service import EmailService
        leader=await UserRepository.get_by_id(team["leaderId"])
        await EmailService.send_email(
            to=leader["email"],
            subject="Registration Approved",
            body="""
        Congratulations! Your Nexora registration has been approved.
        You can now login to the portal.
        Regards,
        Team Nexora
        """
        )

        await UserRepository.update(
            team["leaderId"],
            {
                "status": "Approved",
                "isApproved": True,
                "approvedAt": datetime.utcnow(),
                "approvedBy": "ADMIN"
            }
        )

        await ActivityRepository.create(
            action="APPROVED",
            performed_by="ADMIN",
            team_id=team_id,
            description="Team registration approved."
        )

        await NotificationRepository.create(
            user_id=team["leaderId"],
            title="Registration Approved",
            message="Congratulations! Your registration has been approved."
        )

        return {
            "success": True,
            "message": "Registration approved successfully."
        }

    @staticmethod
    async def reject(team_id: str, remarks: str):

        team = await AdminRepository.registration_details(team_id)

        if not team:
            return {
                "success": False,
                "message": "Team not found."
            }

        await AdminRepository.reject(team_id, remarks)
        leader = await UserRepository.get_by_id(team["leaderId"])
        await EmailService.send_email(
            to=leader["email"],
            subject="Registration Rejected",
            body=f"""
        Your registration has been rejected. 
        Please contact the E-Cell Team.
        Regards,
        Team Nexora
        """
        )
        await UserRepository.update(
            team["leaderId"],
            {
                "status": "Rejected",
                "isApproved": False
            }
        )

        await ActivityRepository.create(
            action="REJECTED",
            performed_by="ADMIN",
            team_id=team_id,
            description="Team registration rejected."
        )

        await NotificationRepository.create(
            user_id=team["leaderId"],
            title="Registration Rejected",
            message="Your registration has been rejected. Please check the remarks."
        )

        return {
            "success": True,
            "message": "Registration rejected successfully."
        }