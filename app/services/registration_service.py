from datetime import datetime, timezone

from app.models.user import create_user
from app.models.team import create_team
from app.models.member import create_member
from app.models.project import create_project

from app.repositories.activity_repository import ActivityRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.team_repository import TeamRepository
from app.repositories.user_repository import UserRepository
from app.repositories.event_repository import EventRepository


class RegistrationService:
    """
    Handles the complete team registration workflow.
    """

    @staticmethod
    async def register(data: dict):

        leader = data["leaderInfo"]
        project = data["projectInfo"]
        verification = data["eCellVerification"]
        team_members = data.get("teamMembers") or []
        event_id = data.get("eventId")

        # -------------------------------------------------
        # Validate dynamic event team size limit set by admin
        # -------------------------------------------------
        if event_id:
            try:
                event = await EventRepository.find_by_id(event_id)
                if event:
                    max_team_size = int(event.get("maxTeamSize", 4))
                    max_additional_members = max(0, max_team_size - 1)
                    if len(team_members) > max_additional_members:
                        return {
                            "success": False,
                            "message": f"This event ({event.get('title')}) allows maximum {max_additional_members} additional team member(s).",
                        }
            except Exception:
                pass

        # -------------------------------------------------
        # Normalize email
        # -------------------------------------------------

        leader_email = leader["email"].strip().lower()

        # -------------------------------------------------
        # Duplicate leader email
        # -------------------------------------------------

        existing_user = await UserRepository.find_by_email(
            leader_email
        )

        if existing_user:
            return {
                "success": False,
                "message": "This email is already registered.",
            }

        # -------------------------------------------------
        # Check duplicate member emails
        # -------------------------------------------------

        member_emails = []

        for member in team_members:
            email = member["memberEmail"].strip().lower()

            if email == leader_email:
                return {
                    "success": False,
                    "message": "Leader email cannot be used again as a team member.",
                }

            if email in member_emails:
                return {
                    "success": False,
                    "message": "Duplicate team member email found.",
                }

            member_emails.append(email)

        # -------------------------------------------------
        # Check member emails against existing users
        # -------------------------------------------------

        for email in member_emails:
            existing_member = await UserRepository.find_by_email(
                email
            )

            if existing_member:
                return {
                    "success": False,
                    "message": f"Team member email {email} is already registered.",
                }

        now = datetime.now(timezone.utc)

        # -------------------------------------------------
        # Create leader
        # -------------------------------------------------

        leader["email"] = leader_email

        leader_doc = await create_user(leader)

        leader_doc["createdAt"] = now
        leader_doc["updatedAt"] = now

        await UserRepository.create(
            leader_doc
        )

        # -------------------------------------------------
        # Create team
        # -------------------------------------------------

        event_id = data.get("eventId") or "EVT-IDEATHON-2026"
        event_name = data.get("eventName") or "Nexora Ideathon 2026"

        team_doc = await create_team(
            leader_doc["userId"],
            project["projectName"].strip(),
        )

        team_doc["eventId"] = event_id
        team_doc["eventName"] = event_name
        team_doc["createdAt"] = now
        team_doc["updatedAt"] = now

        await TeamRepository.create(
            team_doc
        )

        # -------------------------------------------------
        # Create leader member
        # -------------------------------------------------

        leader_member = {
            "memberName": leader["fullName"],
            "memberEmail": leader_email,
            "memberPhone": leader["phone"],
        }

        leader_member_doc = create_member(
            team_doc["teamId"],
            leader_member,
            is_leader=True,
        )

        await MemberRepository.create(
            leader_member_doc
        )

        # -------------------------------------------------
        # Create additional members
        # -------------------------------------------------

        if team_members:

            member_docs = []

            for member in team_members:

                member_data = {
                    "memberName": member["memberName"].strip(),
                    "memberEmail": member["memberEmail"].strip().lower(),
                    "memberPhone": member["memberPhone"],
                }

                member_docs.append(
                    create_member(
                        team_doc["teamId"],
                        member_data,
                        is_leader=False,
                    )
                )

            await MemberRepository.create_many(
                member_docs
            )

        # -------------------------------------------------
        # Create project
        # -------------------------------------------------

        project_doc = await create_project(
            team_doc["teamId"],
            project,
            verification,
        )

        project_doc["eventId"] = event_id
        project_doc["eventName"] = event_name
        project_doc["createdAt"] = now

        await ProjectRepository.create(
            project_doc
        )

        # -------------------------------------------------
        # Notification
        # -------------------------------------------------

        await NotificationRepository.create(
            {
                "userId": leader_doc["userId"],
                "title": "Registration Submitted",
                "message": (
                    "Your NEXORA registration has been submitted "
                    "successfully and is currently under review."
                ),
                "type": "info",
                "isRead": False,
                "createdAt": now,
            }
        )

        # -------------------------------------------------
        # Activity log
        # -------------------------------------------------

        await ActivityRepository.create(
            {
                "userId": leader_doc["userId"],
                "role": "leader",
                "action": "REGISTER",
                "module": "Registration",
                "teamId": team_doc["teamId"],
                "description": "Team registration submitted.",
                "createdAt": now,
            }
        )

        # -------------------------------------------------
        # Final response
        # -------------------------------------------------

        return {
            "success": True,
            "message": "Registration submitted successfully.",
            "teamId": team_doc["teamId"],
            "userId": leader_doc["userId"],
            "status": "Pending",
        }

    @staticmethod
    async def track(identifier: str):
        from app.database.collections import get_collections

        clean_id = identifier.strip()
        collections = get_collections()
        teams = collections["teams"]
        users = collections["users"]
        projects = collections["projects"]
        certificates = collections["certificates"]

        team = None
        # Try search by teamId
        team = await teams.find_one({"teamId": clean_id}, {"_id": 0})

        # If not found by teamId, check if identifier is email
        if not team:
            user = await users.find_one({"email": clean_id.lower()}, {"_id": 0})
            if user:
                team = await teams.find_one({"leaderId": user["userId"]}, {"_id": 0})

        if not team:
            return {
                "success": False,
                "message": "No registration found with this Team ID or Email.",
            }

        leader = await users.find_one({"userId": team.get("leaderId")}, {"_id": 0})
        project = await projects.find_one({"teamId": team.get("teamId")}, {"_id": 0})
        cert = await certificates.find_one({"teamId": team.get("teamId")}, {"_id": 0})

        return {
            "success": True,
            "message": "Registration record found.",
            "data": {
                "teamId": team.get("teamId"),
                "teamName": team.get("teamName"),
                "status": team.get("status", "Pending"),
                "remarks": team.get("remarks"),
                "createdAt": team.get("createdAt"),
                "leaderName": leader.get("fullName") if leader else "—",
                "projectName": project.get("projectName") if project else team.get("teamName"),
                "domain": project.get("domain") if project else "—",
                "stage": project.get("stage") if project else "—",
                "certificateId": cert.get("certificateId") if cert else None,
                "hasCertificate": bool(cert),
            }
        }