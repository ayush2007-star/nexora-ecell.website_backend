from datetime import datetime, timezone
from uuid import uuid4

from app.repositories.admin_repository import AdminRepository
from app.repositories.certificate_repository import CertificateRepository
from app.database.collections import get_collections


class CertificateService:

    @staticmethod
    async def generate(team_id: str, options: dict = None):
        options = options or {}

        # ---------------------------------------------
        # Get registration
        # ---------------------------------------------
        registration = await AdminRepository.registration_details(team_id)

        if not registration:
            raise ValueError("Team not found.")

        team = registration["team"]
        leader = registration.get("leader")
        project = registration.get("project") or {}
        members = registration.get("members") or []

        # ---------------------------------------------
        # Certificate only for approved teams
        # ---------------------------------------------
        if team.get("status") != "Approved":
            raise ValueError("Certificate can only be generated for an approved team.")

        # ---------------------------------------------
        # Check existing certificate
        # ---------------------------------------------
        existing = await CertificateRepository.get_by_team(team_id)

        now = datetime.now(timezone.utc)
        certificate_id = existing.get("certificateId") if existing else f"NXR-{uuid4().hex[:12].upper()}"

        theme = options.get("theme") or (existing.get("theme") if existing else "gold")
        title = options.get("title") or (existing.get("title") if existing else "Certificate of Excellence")
        event_title = options.get("eventTitle") or (
            existing.get("eventTitle")
            if existing and existing.get("eventTitle")
            else team.get("eventName") or "NEXORA Innovation Initiative 2026"
        )
        issuer_name = options.get("issuerName") or (existing.get("issuerName") if existing else "Prof. A. K. Sharma")
        issuer_title = options.get("issuerTitle") or (
            existing.get("issuerTitle") if existing else "Convener & Head of Incubation"
        )
        custom_message = options.get("customMessage") or (
            existing.get("customMessage")
            if existing
            else "In recognition of outstanding innovative thinking, active problem-solving, and dedication to entrepreneurial excellence."
        )

        member_names = [m.get("memberName") for m in members if m.get("memberName")]

        certificate = {
            "certificateId": certificate_id,
            "teamId": team_id,
            "teamName": team.get("teamName"),
            "projectName": project.get("projectName", team.get("teamName")),
            "domain": project.get("domain", "Technology & Innovation"),
            "eventId": team.get("eventId", "EVT-IDEATHON-2026"),
            "eventTitle": event_title,
            "leaderName": (leader.get("fullName") if leader else "Participant"),
            "leaderEmail": (leader.get("email") if leader else None),
            "college": (leader.get("college") if leader else None),
            "memberNames": member_names,
            "theme": theme,
            "title": title,
            "issuerName": issuer_name,
            "issuerTitle": issuer_title,
            "customMessage": custom_message,
            "generatedAt": existing.get("generatedAt") if existing else now,
            "updatedAt": now,
            "status": "Generated",
        }

        if existing:
            col = get_collections()["certificates"]
            if col is not None:
                await col.update_one({"certificateId": certificate_id}, {"$set": certificate})
        else:
            await CertificateRepository.create(certificate)

        return certificate

    @staticmethod
    async def bulk_generate(event_id: str, options: dict = None):
        options = options or {}
        teams_col = get_collections()["teams"]
        if teams_col is None:
            return {"count": 0, "certificates": []}

        filter_query = {"status": "Approved"}
        if event_id and event_id.upper() != "ALL":
            filter_query["$or"] = [{"eventId": event_id}, {"event": event_id}]

        cursor = teams_col.find(filter_query)
        generated_list = []

        async for team in cursor:
            team_id = team.get("teamId")
            if team_id:
                try:
                    cert = await CertificateService.generate(team_id, options)
                    generated_list.append(cert)
                except Exception:
                    continue

        return {"count": len(generated_list), "certificates": generated_list}

    @staticmethod
    async def verify(certificate_id: str):
        certificate = await CertificateRepository.get_by_certificate_id(certificate_id)
        if not certificate:
            return None
        return certificate

    @staticmethod
    async def get_by_team(team_id: str):
        certificate = await CertificateRepository.get_by_team(team_id)
        if not certificate:
            return None
        return certificate