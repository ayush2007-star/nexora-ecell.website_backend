from datetime import datetime, timezone
import logging
from uuid import uuid4

from app.email.email_service import EmailService
from app.repositories.activity_repository import ActivityRepository
from app.repositories.admin_repository import AdminRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.team_repository import TeamRepository
from app.repositories.project_repository import ProjectRepository
from app.models.member import create_member
from app.models.team import create_team
from app.models.project import create_project
from app.core.security import hash_password

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

    # -------------------------------------------------------------
    # TEAM MEMBER MANAGEMENT
    # -------------------------------------------------------------

    @staticmethod
    async def add_team_member(team_id: str, member_data: dict, admin_user: dict):
        team_data = await AdminRepository.registration_details(team_id)
        if not team_data:
            return {"success": False, "message": "Team registration not found."}

        existing_members = team_data.get("members") or []
        if len(existing_members) >= 5:
            return {"success": False, "message": "Maximum 5 team members limit reached for this team."}

        new_member = create_member(team_id, member_data, is_leader=False)
        await MemberRepository.create(new_member)

        now = datetime.now(timezone.utc)
        await ActivityRepository.create({
            "userId": admin_user.get("userId"),
            "role": "admin",
            "action": "ADDED_MEMBER",
            "module": "TeamMember",
            "teamId": team_id,
            "description": f"Added team member {new_member.get('memberName')}.",
            "createdAt": now,
        })

        return {
            "success": True,
            "message": "Team member added successfully.",
            "data": new_member
        }

    @staticmethod
    async def update_team_member(team_id: str, member_id: str, member_data: dict, admin_user: dict):
        updated = await MemberRepository.update_member(team_id, member_id, member_data)
        if not updated:
            return {"success": False, "message": "Failed to update team member or member not found."}

        now = datetime.now(timezone.utc)
        await ActivityRepository.create({
            "userId": admin_user.get("userId"),
            "role": "admin",
            "action": "UPDATED_MEMBER",
            "module": "TeamMember",
            "teamId": team_id,
            "description": f"Updated team member {member_id}.",
            "createdAt": now,
        })

        return {
            "success": True,
            "message": "Team member updated successfully."
        }

    @staticmethod
    async def delete_team_member(team_id: str, member_id: str, admin_user: dict):
        deleted = await MemberRepository.delete_member(team_id, member_id)
        if not deleted or deleted.deleted_count == 0:
            return {"success": False, "message": "Member not found or already deleted."}

        now = datetime.now(timezone.utc)
        await ActivityRepository.create({
            "userId": admin_user.get("userId"),
            "role": "admin",
            "action": "DELETED_MEMBER",
            "module": "TeamMember",
            "teamId": team_id,
            "description": f"Deleted member {member_id} from team {team_id}.",
            "createdAt": now,
        })

        return {
            "success": True,
            "message": "Team member deleted successfully."
        }

    # -------------------------------------------------------------
    # DIRECT REGISTRATION BY ADMIN
    # -------------------------------------------------------------

    @staticmethod
    async def direct_register_team(event_id: str, payload: dict, admin_user: dict):
        """
        Direct registration of a team with leader and optional members by an admin.
        """
        now = datetime.now(timezone.utc)
        team_id = f"NXR-TM-{uuid4().hex[:6].upper()}"
        leader_id = f"USR-{uuid4().hex[:6].upper()}"
        project_id = f"PRJ-{uuid4().hex[:6].upper()}"

        leader_name = payload.get("leaderName", "").strip() or "Team Leader"
        leader_email = payload.get("leaderEmail", "").strip().lower()
        leader_phone = str(payload.get("leaderPhone", "")).strip() or "9876543210"
        team_name = payload.get("teamName", "").strip() or f"{leader_name}'s Team"
        project_name = payload.get("projectName", "").strip() or team_name
        domain = payload.get("domain", "Technology & Innovation")
        stage = payload.get("stage", "Prototype / MVP")
        description = payload.get("description", "Directly added by Administrator.")

        # Create Leader User
        existing_user = await UserRepository.find_by_email(leader_email)
        if existing_user:
            leader_user_id = existing_user["userId"]
        else:
            leader_user = {
                "userId": leader_id,
                "fullName": leader_name,
                "email": leader_email,
                "phone": leader_phone,
                "college": payload.get("college", "Nexora Innovation Campus"),
                "department": payload.get("department", "Engineering"),
                "year": payload.get("year", "4th Year"),
                "rollNumber": payload.get("rollNumber", "NXR-DIR-01"),
                "role": "leader",
                "password": hash_password("Nexora@2026"),
                "status": "Approved",
                "isApproved": True,
                "approvedBy": admin_user.get("userId"),
                "approvedAt": now,
                "isActive": True,
                "createdAt": now,
                "updatedAt": now,
            }
            await UserRepository.create(leader_user)
            leader_user_id = leader_id

        # Create Team
        team_doc = {
            "teamId": team_id,
            "teamName": team_name,
            "leaderId": leader_user_id,
            "eventId": event_id,
            "eventName": payload.get("eventName", "Nexora Innovation Event"),
            "status": "Approved",
            "remarks": "Directly registered and pre-approved by Admin.",
            "createdAt": now,
            "updatedAt": now,
        }
        await TeamRepository.create(team_doc)

        # Create Project
        project_doc = {
            "projectId": project_id,
            "teamId": team_id,
            "projectName": project_name,
            "domain": domain,
            "stage": stage,
            "description": description,
            "eurekaTeamId": payload.get("eurekaTeamId", "DIR-ADMIN"),
            "referralCodeUsed": payload.get("referralCodeUsed", "ADMIN"),
            "pitchDeckUrl": payload.get("pitchDeckUrl", ""),
            "createdAt": now,
            "updatedAt": now,
        }
        await ProjectRepository.create(project_doc)

        # Create Team Members
        raw_members = payload.get("members") or []
        created_members = []
        for mem in raw_members:
            if mem.get("memberName") or mem.get("name"):
                m_doc = create_member(team_id, mem, is_leader=False)
                await MemberRepository.create(m_doc)
                created_members.append(m_doc)

        # Log Activity
        await ActivityRepository.create({
            "userId": admin_user.get("userId"),
            "role": "admin",
            "action": "DIRECT_REGISTERED",
            "module": "Registration",
            "teamId": team_id,
            "description": f"Directly registered team {team_name} for event {event_id}.",
            "createdAt": now,
        })

        return {
            "success": True,
            "message": "Team directly registered and approved successfully!",
            "data": {
                "teamId": team_id,
                "teamName": team_name,
                "leaderName": leader_name,
                "leaderEmail": leader_email,
                "eventId": event_id,
                "membersCount": len(created_members),
                "status": "Approved"
            }
        }