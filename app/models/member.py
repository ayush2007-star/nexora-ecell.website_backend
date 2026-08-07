from datetime import datetime


def create_member(
    team_id: str,
    data: dict,
    is_leader=False
):

    return {

        "teamId": team_id,

        "memberName": data["memberName"],

        "memberEmail": data["memberEmail"].lower(),

        "memberPhone": data["memberPhone"],

        "isLeader": is_leader,

        "createdAt": datetime.utcnow()
    }
