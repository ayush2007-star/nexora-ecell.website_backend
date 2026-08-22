from datetime import datetime, timezone

from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token
from app.database.collections import get_collections


class AuthService:

    # =========================================================
    # SET PASSWORD - PARTICIPANTS
    # =========================================================

    @staticmethod
    async def set_password(data):

        email = (data.get("email") or "").strip().lower()
        password = (data.get("password") or "").strip()

        if len(password) < 8:
            return {
                "success": False,
                "message": "Password must contain at least 8 characters.",
            }

        user = await UserRepository.find_by_email(email)

        if not user:
            return {
                "success": False,
                "message": "No registered account found with this email.",
            }

        role = str(
            user.get("role", "")
        ).strip().lower()

        if role not in [
            "leader",
            "student",
            "participant",
        ]:
            return {
                "success": False,
                "message": (
                    "Password setup is only available "
                    "for participant accounts."
                ),
            }

        if not user.get("isApproved"):
            return {
                "success": False,
                "message": "Your registration is not approved yet.",
            }

        now = datetime.now(timezone.utc)

        await UserRepository.update(
            user["userId"],
            {
                "password": hash_password(password),
                "passwordSet": True,
                "passwordSetAt": now,
                "updatedAt": now,
            },
        )

        return {
            "success": True,
            "message": (
                "Password created successfully. "
                "You can now login."
            ),
        }

    # =========================================================
    # LOGIN
    # =========================================================

    @staticmethod
    async def login(data):

        identifier = (
            data.get("email") or ""
        ).strip().lower()

        password = (
            data.get("password") or ""
        ).strip()

        if not identifier or not password:
            return {
                "success": False,
                "message": (
                    "Email / Team ID and password "
                    "are required."
                ),
            }

        # =====================================================
        # FIND USER BY EMAIL
        # =====================================================

        user = await UserRepository.find_by_email(
            identifier
        )

        # =====================================================
        # TEAM ID / EUREKA TEAM ID LOGIN
        # =====================================================

        if not user:

            try:

                collections = get_collections()

                teams_col = collections["teams"]
                projects_col = collections["projects"]

                team = await teams_col.find_one(
                    {
                        "teamId": identifier.upper()
                    }
                )

                # -------------------------------------------------
                # Eureka Team ID
                # -------------------------------------------------

                if not team:

                    project = await projects_col.find_one(
                        {
                            "eurekaTeamId": identifier
                        }
                    )

                    if project:

                        team = await teams_col.find_one(
                            {
                                "teamId": project.get(
                                    "teamId"
                                )
                            }
                        )

                # -------------------------------------------------
                # Team leader becomes login user
                # -------------------------------------------------

                if team and team.get("leaderId"):

                    user = await UserRepository.find_by_user_id(
                        team["leaderId"]
                    )

            except Exception:

                return {
                    "success": False,
                    "message": (
                        "Unable to connect to the database."
                    ),
                }

        # =====================================================
        # USER NOT FOUND
        # =====================================================

        if not user:

            return {
                "success": False,
                "message": (
                    "Invalid email, Team ID, or password."
                ),
            }

        # =====================================================
        # ACCOUNT STATUS
        # =====================================================

        if user.get("isActive") is False:

            return {
                "success": False,
                "message": (
                    "This account has been disabled. "
                    "Please contact admin."
                ),
            }

        role = str(
            user.get("role", "leader")
        ).strip().lower()

        # =====================================================
        # PARTICIPANT / STUDENT / LEADER
        # =====================================================

        if role in [
            "leader",
            "student",
            "participant",
        ]:

            if not user.get("isApproved"):

                return {
                    "success": False,
                    "message": (
                        "Your registration is still "
                        "pending approval."
                    ),
                }

            stored_password = user.get(
                "password"
            )

            if not stored_password:

                return {
                    "success": False,
                    "message": (
                        "Password is not set yet. "
                        "Please use Set Password first."
                    ),
                    "code": "PASSWORD_NOT_SET",
                }

            if not verify_password(
                password,
                stored_password,
            ):

                return {
                    "success": False,
                    "message": (
                        "Invalid email / Team ID "
                        "or password."
                    ),
                }

            # -------------------------------------------------
            # IMPORTANT:
            # Keep existing frontend compatibility.
            # Participant login continues returning leader.
            # -------------------------------------------------

            token = create_access_token(
                {
                    "userId": user["userId"],
                    "role": "leader",
                    "fullName": user.get(
                        "fullName",
                        "Participant",
                    ),
                    "email": user.get(
                        "email"
                    ),
                }
            )

            return {
                "success": True,
                "message": (
                    "Participant login successful."
                ),
                "token": token,
                "user": {
                    "userId": user["userId"],
                    "fullName": user.get(
                        "fullName",
                        "Participant",
                    ),
                    "email": user.get(
                        "email"
                    ),
                    "role": "leader",
                },
            }

        # =====================================================
        # MENTOR / JUDGE
        # =====================================================

        if role == "mentor":

            stored_password = user.get(
                "password"
            )

            if not stored_password:

                return {
                    "success": False,
                    "message": (
                        "Mentor password is not configured. "
                        "Please contact admin."
                    ),
                }

            if not verify_password(
                password,
                stored_password,
            ):

                return {
                    "success": False,
                    "message": (
                        "Invalid mentor email "
                        "or password."
                    ),
                }

            token = create_access_token(
                {
                    "userId": user["userId"],
                    "role": "mentor",
                    "mentorIndex": user.get(
                        "mentorIndex",
                        1,
                    ),
                    "fullName": user.get(
                        "fullName",
                        "Mentor",
                    ),
                    "email": user.get(
                        "email"
                    ),
                }
            )

            return {
                "success": True,
                "message": (
                    "Mentor login successful."
                ),
                "token": token,
                "user": {
                    "userId": user["userId"],
                    "fullName": user.get(
                        "fullName",
                        "Mentor",
                    ),
                    "email": user.get(
                        "email"
                    ),
                    "role": "mentor",
                    "mentorIndex": user.get(
                        "mentorIndex",
                        1,
                    ),
                    "specialization": user.get(
                        "department",
                        user.get(
                            "specialization",
                            "Startup Mentor / Jury",
                        ),
                    ),
                },
            }

        # =====================================================
        # MANAGEMENT
        # =====================================================

        if role == "management":

            stored_password = user.get(
                "password"
            )

            if not stored_password:

                return {
                    "success": False,
                    "message": (
                        "Management password is not configured. "
                        "Please contact admin."
                    ),
                }

            if not verify_password(
                password,
                stored_password,
            ):

                return {
                    "success": False,
                    "message": (
                        "Invalid management email "
                        "or password."
                    ),
                }

            if user.get("isActive") is False:

                return {
                    "success": False,
                    "message": (
                        "This management account "
                        "is currently inactive."
                    ),
                }

            token = create_access_token(
                {
                    "userId": user["userId"],
                    "role": "management",
                    "fullName": user.get(
                        "fullName",
                        "Management",
                    ),
                    "email": user.get(
                        "email"
                    ),
                    "department": user.get(
                        "department",
                        "Event Management",
                    ),
                    "designation": user.get(
                        "designation",
                        "Management Staff",
                    ),
                }
            )

            return {
                "success": True,
                "message": (
                    "Management login successful."
                ),
                "token": token,
                "user": {
                    "userId": user["userId"],
                    "fullName": user.get(
                        "fullName",
                        "Management",
                    ),
                    "email": user.get(
                        "email"
                    ),
                    "role": "management",
                    "department": user.get(
                        "department",
                        "Event Management",
                    ),
                    "designation": user.get(
                        "designation",
                        "Management Staff",
                    ),
                },
            }

        # =====================================================
        # ADMIN
        # =====================================================

        if role == "admin":

            stored_password = user.get(
                "password"
            )

            if not stored_password:

                return {
                    "success": False,
                    "message": (
                        "Admin password is not configured."
                    ),
                }

            if not verify_password(
                password,
                stored_password,
            ):

                return {
                    "success": False,
                    "message": (
                        "Invalid admin email "
                        "or password."
                    ),
                }

            token = create_access_token(
                {
                    "userId": user["userId"],
                    "role": "admin",
                    "fullName": user.get(
                        "fullName",
                        "Administrator",
                    ),
                    "email": user.get(
                        "email"
                    ),
                }
            )

            return {
                "success": True,
                "message": (
                    "Admin login successful."
                ),
                "token": token,
                "user": {
                    "userId": user["userId"],
                    "fullName": user.get(
                        "fullName",
                        "Administrator",
                    ),
                    "email": user.get(
                        "email"
                    ),
                    "role": "admin",
                },
            }

        # =====================================================
        # UNKNOWN ROLE
        # =====================================================

        return {
            "success": False,
            "message": (
                "This account has an unsupported role. "
                "Please contact admin."
            ),
        }