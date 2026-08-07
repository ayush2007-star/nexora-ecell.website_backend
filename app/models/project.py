from datetime import datetime

from app.utils.id_generator import generate_project_id


async def create_project(
    team_id: str,
    data: dict,
    verification: dict
):

    project_id = await generate_project_id()

    return {

        "projectId": project_id,

        "teamId": team_id,

        "projectName": data["projectName"],

        "domain": data["domain"],

        "description": data["description"],

        "stage": data["stage"],

        "eurekaTeamId": verification["eurekaTeamId"],

        "referralCodeUsed": verification.get(
            "referralCodeUsed"
        ),

        "pitchDeckUrl": verification.get(
            "pitchDeckUrl"
        ),

        "status": "Pending",

        "createdAt": datetime.utcnow()
    }
