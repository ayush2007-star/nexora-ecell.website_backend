import uuid
from datetime import datetime

from app.repositories.certificate_repository import CertificateRepository


class CertificateService:

    @staticmethod
    async def generate(team_id: str):

        certificate = {

            "certificateId": str(uuid.uuid4())[:12].upper(),

            "teamId": team_id,

            "generatedAt": datetime.utcnow(),

            "status": "Generated"

        }

        await CertificateRepository.create(certificate)

        return certificate

    @staticmethod
    async def verify(certificate_id: str):

        return await CertificateRepository.get_by_certificate_id(
            certificate_id
        )