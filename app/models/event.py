from datetime import datetime, timezone
from uuid import uuid4


def create_event(data: dict) -> dict:
    now = datetime.now(timezone.utc)
    custom_id = data.get("eventId")
    event_id = custom_id.strip() if custom_id else f"EVT-{uuid4().hex[:8].upper()}"

    return {
        "eventId": event_id,
        "title": data.get("title", "").strip(),
        "category": data.get("category", "Hackathon").strip(),
        "badge": data.get("badge", "FLAGSHIP EVENT").strip(),
        "date": data.get("date", "").strip(),
        "venue": data.get("venue", "Main Campus / Hybrid").strip(),
        "description": data.get("description", "").strip(),
        "prizePool": data.get("prizePool", "₹1,00,000+").strip(),
        "maxTeamSize": int(data.get("maxTeamSize", 3)),
        "registrationDeadline": data.get("registrationDeadline", "").strip(),
        "status": data.get("status", "Live").strip(),
        "bannerUrl": data.get("bannerUrl"),
        "createdAt": now,
        "updatedAt": now,
    }
