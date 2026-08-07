from datetime import datetime

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


class RegistrationService:

    @staticmethod
    async def register(data):

        leader = data["leaderInfo"]
        project = data["projectInfo"]
        verification = data["eCellVerification"]
        team_members = data.get("teamMembers", [])

        # ---------------------------------------
        # Email Already Exists
        # ---------------------------------------

        existing_user = await UserRepository.find_by_email(
            leader["email"]
        )

        if existing_user:
            return {
                "success": False,
                "message": "Email already registered."
            }

        # ---------------------------------------
        # Create Leader
        # ---------------------------------------

        leader_doc = await create_user(leader)

        leader_result = await UserRepository.create(
            leader_doc
        )

        # ---------------------------------------
        # Create Team
        # ---------------------------------------

        team_doc = await create_team(
            leader_doc["userId"],
            project["projectName"]
        )

        await TeamRepository.create(team_doc)

        # ---------------------------------------
        # Save Leader in Members Collection
        # ---------------------------------------

        await MemberRepository.create(
            {
                "teamId": team_doc["teamId"],
                "memberName": leader["fullName"],
                "memberEmail": leader["email"],
                "memberPhone": leader["phone"],
                "isLeader": True,
                "createdAt": datetime.utcnow(),
            }
        )

        # ---------------------------------------
        # Save Other Members
        # ---------------------------------------

        if team_members:

            member_docs = []

            for member in team_members:

                member_docs.append(
                    create_member(
                        team_doc["teamId"],
                        member
                    )
                )

            await MemberRepository.create_many(
                member_docs
            )

        # ---------------------------------------
        # Create Project
        # ---------------------------------------

        project_doc = await create_project(
            team_doc["teamId"],
            project,
            verification
        )

        await ProjectRepository.create(project_doc)

        # ---------------------------------------
        # Notification
        # ---------------------------------------

        await NotificationRepository.create(
            {
                "userId": leader_doc["userId"],
                "title": "Registration Submitted",
                "message": "Your registration is under review.",
                "type": "info",
                "isRead": False,
                "createdAt": datetime.utcnow()
            }
        )

        # ---------------------------------------
        # Activity Log
        # ---------------------------------------

        await ActivityRepository.create(
            {
                "userId": leader_doc["userId"],
                "role": "leader",
                "action": "REGISTER",
                "module": "Registration",
                "description": "Team registration submitted.",
                "createdAt": datetime.utcnow()
            }
        )

        # ---------------------------------------
        # Response
        # ---------------------------------------

        return {
            "success": True,
            "message": "Registration submitted successfully.",
            "teamId": team_doc["teamId"],
            "userId": leader_doc["userId"]
        }
