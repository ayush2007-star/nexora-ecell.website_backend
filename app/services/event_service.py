from datetime import datetime, timezone
from app.models.event import create_event
from app.repositories.event_repository import EventRepository
from app.database.collections import get_collections


class EventService:

    @staticmethod
    async def get_public_events():
        events = await EventRepository.find_public()
        if not events:
            # Seed initial default events if none exist
            defaults = [
                {
                    "eventId": "EVT-IDEATHON-2026",
                    "title": "Nexora Ideathon 2026",
                    "category": "Flagship Hackathon",
                    "badge": "FLAGSHIP EVENT",
                    "date": "September 15-17, 2026",
                    "venue": "Main Innovation Auditorium & Online",
                    "description": "48-hour intensive problem solving and product building challenge. Build prototypes and pitch directly to angel investors.",
                    "prizePool": "₹2,50,000",
                    "maxTeamSize": 3,
                    "registrationDeadline": "September 10, 2026",
                    "status": "Live",
                },
                {
                    "eventId": "EVT-BOOTCAMP-2026",
                    "title": "Founders Bootcamp & Pitch Lab",
                    "category": "Workshop & Accelerator",
                    "badge": "WORKSHOP SERIES",
                    "date": "October 05, 2026",
                    "venue": "Nexora Incubation Center",
                    "description": "Learn from venture capitalists and unicorn founders how to craft high-conversion pitch decks, product unit economics, and growth flywheels.",
                    "prizePool": "Incubation Grants",
                    "maxTeamSize": 3,
                    "registrationDeadline": "October 01, 2026",
                    "status": "Upcoming",
                },
                {
                    "eventId": "EVT-ESUMMIT-2026",
                    "title": "Nexora E-Summit & Pitch Battle",
                    "category": "Annual Grand Summit",
                    "badge": "ANNUAL SUMMIT",
                    "date": "November 20-22, 2026",
                    "venue": "Grand Convention Hall",
                    "description": "Annual flagship summit bringing together 50+ speakers, 100+ student startups, and ₹5,00,000+ in seed prize pools and investor term sheets.",
                    "prizePool": "₹5,00,000",
                    "maxTeamSize": 3,
                    "registrationDeadline": "November 12, 2026",
                    "status": "Upcoming",
                },
            ]
            for d in defaults:
                doc = create_event(d)
                await EventRepository.create(doc)
            events = await EventRepository.find_public()

        return events

    @staticmethod
    async def get_all_events():
        events = await EventRepository.find_all()
        if not events:
            await EventService.get_public_events()
            events = await EventRepository.find_all()
        return events

    @staticmethod
    async def get_event_details(event_id: str):
        event = await EventRepository.find_by_id(event_id)
        if not event:
            raise ValueError(f"Event with ID '{event_id}' not found.")
        return event

    @staticmethod
    async def create_new_event(data: dict):
        if not data.get("title", "").strip():
            raise ValueError("Event title is required.")

        doc = create_event(data)
        await EventRepository.create(doc)
        return doc

    @staticmethod
    async def update_event(event_id: str, data: dict):
        existing = await EventRepository.find_by_id(event_id)
        if not existing:
            raise ValueError(f"Event '{event_id}' not found.")

        updated = await EventRepository.update(event_id, data)
        return updated

    @staticmethod
    async def delete_event(event_id: str):
        existing = await EventRepository.find_by_id(event_id)
        if not existing:
            raise ValueError(f"Event '{event_id}' not found.")

        deleted = await EventRepository.delete(event_id)
        return deleted

    @staticmethod
    async def get_event_registrations(event_id: str):
        teams_col = get_collections()["teams"]
        if teams_col is None:
            return []

        # Find registrations specifically for this event ID
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"eventId": event_id},
                        {"event": event_id},
                        {"project.eventId": event_id}
                    ]
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "leaderId",
                    "foreignField": "userId",
                    "as": "leaderInfo"
                }
            },
            {
                "$lookup": {
                    "from": "projects",
                    "localField": "teamId",
                    "foreignField": "teamId",
                    "as": "projectInfo"
                }
            },
            {
                "$lookup": {
                    "from": "certificates",
                    "localField": "teamId",
                    "foreignField": "teamId",
                    "as": "certInfo"
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "teamId": 1,
                    "teamName": 1,
                    "eventId": 1,
                    "eventName": 1,
                    "status": 1,
                    "remarks": 1,
                    "createdAt": 1,
                    "leader": {"$arrayElemAt": ["$leaderInfo", 0]},
                    "project": {"$arrayElemAt": ["$projectInfo", 0]},
                    "certificate": {"$arrayElemAt": ["$certInfo", 0]}
                }
            },
            {"$sort": {"createdAt": -1}}
        ]

        cursor = teams_col.aggregate(pipeline)
        results = []
        async for doc in cursor:
            # Flatten leader details
            leader = doc.get("leader") or {}
            project = doc.get("project") or {}
            certificate = doc.get("certificate")

            doc["leaderName"] = leader.get("fullName", "—")
            doc["leaderEmail"] = leader.get("email", "—")
            doc["leaderPhone"] = leader.get("phone", "—")
            doc["college"] = leader.get("college", "—")
            doc["projectName"] = project.get("projectName", doc.get("teamName", "—"))
            doc["domain"] = project.get("domain", "—")
            doc["certificateId"] = certificate.get("certificateId") if certificate else None

            results.append(doc)

        return results
