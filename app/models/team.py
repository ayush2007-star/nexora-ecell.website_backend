from datetime import datetime

from app.utils.id_generator import generate_team_id


async def create_team(
    leader_id: str,
    project_name: str
):

    team_id = await generate_team_id()

    return {

        "teamId": team_id,

        "teamName": project_name,

        "leaderId": leader_id,

        "status": "Pending",

        "remarks": None,

        "createdAt": datetime.utcnow(),

        "updatedAt": datetime.utcnow()
    }
