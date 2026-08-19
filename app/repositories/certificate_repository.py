from app.database.collections import get_collections


class CertificateRepository:

    @staticmethod
    async def create(document: dict):
        certificates = get_collections()["certificates"]

        return await certificates.insert_one(document)

    @staticmethod
    async def get_by_team(team_id: str):
        certificates = get_collections()["certificates"]

        return await certificates.find_one(
            {"teamId": team_id},
            {"_id": 0},
        )

    @staticmethod
    async def get_by_certificate_id(
        certificate_id: str,
    ):
        certificates = get_collections()["certificates"]

        return await certificates.find_one(
            {"certificateId": certificate_id},
            {"_id": 0},
        )