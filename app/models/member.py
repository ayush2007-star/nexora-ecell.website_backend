from datetime import datetime, timezone
from uuid import uuid4


def create_member(
    team_id: str,
    data: dict,
    is_leader=False
):
    member_id = data.get("memberId") or f"MEM-{uuid4().hex[:8].upper()}"

    return {
        "memberId": member_id,
        "teamId": team_id,
        "memberName": data.get("memberName") or data.get("name", ""),
        "memberEmail": (data.get("memberEmail") or data.get("email", "")).lower().strip(),
        "memberPhone": str(data.get("memberPhone") or data.get("phone", "")).strip(),
        "role": data.get("role", "Member"),
        "isLeader": is_leader,
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }
