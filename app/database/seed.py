import logging
from datetime import datetime, timezone
from app.database.collections import get_collections
from app.core.security import hash_password
from app.models.event import create_event

logger = logging.getLogger(__name__)

ADMIN_EMAIL = "bakt.2007@gmail.com"
ADMIN_NAME = "Ayush Tripathi"
ADMIN_PASSWORD_RAW = "Ayush@2007"
ADMIN_PHONE = "9876543210"


async def seed_admin_user():
    """
    Ensure the super admin account (Ayush Tripathi - bakt.2007@gmail.com)
    is created and active with full administrative credentials.
    """
    try:
        collections = get_collections()
        users = collections.get("users")
        if users is None:
            logger.warning("MongoDB not ready: skipped admin seeding.")
            return

        now = datetime.now(timezone.utc)
        existing_admin = await users.find_one({"email": ADMIN_EMAIL.lower()})

        hashed_pwd = hash_password(ADMIN_PASSWORD_RAW)

        if not existing_admin:
            admin_doc = {
                "userId": "ADMIN-AYUSH-2007",
                "fullName": ADMIN_NAME,
                "email": ADMIN_EMAIL.lower(),
                "phone": ADMIN_PHONE,
                "college": "Nexora Innovation Hub",
                "department": "Entrepreneurship & Technology",
                "year": "Admin",
                "rollNumber": "NXR-ADMIN-01",
                "role": "admin",
                "password": hashed_pwd,
                "status": "Approved",
                "isApproved": True,
                "approvedBy": "SYSTEM",
                "approvedAt": now,
                "isActive": True,
                "createdAt": now,
                "updatedAt": now,
            }
            await users.insert_one(admin_doc)
            logger.info("✅ Super Admin (%s) created successfully.", ADMIN_EMAIL)
        else:
            # Update password and role to ensure admin login always works
            await users.update_one(
                {"_id": existing_admin["_id"]},
                {
                    "$set": {
                        "fullName": ADMIN_NAME,
                        "role": "admin",
                        "password": hashed_pwd,
                        "status": "Approved",
                        "isApproved": True,
                        "isActive": True,
                        "updatedAt": now,
                    }
                },
            )
            logger.info("✅ Super Admin (%s) credentials verified and active.", ADMIN_EMAIL)
    except Exception as e:
        logger.warning("Notice during admin seeding: %s", e)


async def seed_default_events():
    """
    Seed initial flagship events if event collection is empty.
    """
    try:
        collections = get_collections()
        events = collections.get("events")
        if events is None:
            return

        count = await events.count_documents({})
        if count == 0:
            default_events = [
                {
                    "eventId": "EVT-IDEATHON-2026",
                    "title": "Nexora Ideathon 2026",
                    "category": "Flagship Hackathon",
                    "badge": "FLAGSHIP EVENT",
                    "date": "September 15-17, 2026",
                    "venue": "Main Innovation Auditorium & Online",
                    "description": "48-hour intensive problem solving and prototype building challenge. Pitch directly before angel investors and venture incubators.",
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
                    "description": "Masterclass series with unicorn founders and venture capitalists on high-conversion pitch decks, product unit economics, and growth flywheels.",
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
                    "description": "Annual flagship summit bringing together 50+ speakers, 100+ student startups, and ₹5,00,000+ in seed prize pools and term sheets.",
                    "prizePool": "₹5,00,000",
                    "maxTeamSize": 3,
                    "registrationDeadline": "November 12, 2026",
                    "status": "Upcoming",
                },
            ]
            for ev in default_events:
                doc = create_event(ev)
                await events.insert_one(doc)
            logger.info("✅ Default events seeded successfully.")
    except Exception as e:
        logger.warning("Notice during event seeding: %s", e)


async def seed_mentor_users():
    """
    Ensure the 4 Mentor / Judge accounts are created and active:
    Mentor 1: mentor1@nexora-ecell.in (ID: MENTOR-01, Default Pass: Mentor1@2026)
    Mentor 2: mentor2@nexora-ecell.in (ID: MENTOR-02, Default Pass: Mentor2@2026)
    Mentor 3: mentor3@nexora-ecell.in (ID: MENTOR-03, Default Pass: Mentor3@2026)
    Mentor 4: mentor4@nexora-ecell.in (ID: MENTOR-04, Default Pass: Mentor4@2026)
    """
    try:
        collections = get_collections()
        users = collections.get("users")
        if users is None:
            return

        now = datetime.now(timezone.utc)

        mentors = [
            {
                "userId": "MENTOR-01",
                "fullName": "Mentor 1 (Judge 1)",
                "email": "mentor1@nexora-ecell.in",
                "passwordRaw": "Mentor1@2026",
                "role": "mentor",
                "mentorIndex": 1,
            },
            {
                "userId": "MENTOR-02",
                "fullName": "Mentor 2 (Judge 2)",
                "email": "mentor2@nexora-ecell.in",
                "passwordRaw": "Mentor2@2026",
                "role": "mentor",
                "mentorIndex": 2,
            },
            {
                "userId": "MENTOR-03",
                "fullName": "Mentor 3 (Judge 3)",
                "email": "mentor3@nexora-ecell.in",
                "passwordRaw": "Mentor3@2026",
                "role": "mentor",
                "mentorIndex": 3,
            },
            {
                "userId": "MENTOR-04",
                "fullName": "Mentor 4 (Judge 4)",
                "email": "mentor4@nexora-ecell.in",
                "passwordRaw": "Mentor4@2026",
                "role": "mentor",
                "mentorIndex": 4,
            },
        ]

        for m in mentors:
            existing = await users.find_one({"email": m["email"].lower()})
            hashed_pwd = hash_password(m["passwordRaw"])
            if not existing:
                doc = {
                    "userId": m["userId"],
                    "fullName": m["fullName"],
                    "email": m["email"].lower(),
                    "phone": "9876543210",
                    "college": "Nexora Jury Panel",
                    "department": "Jury & Mentorship",
                    "year": "Judge",
                    "rollNumber": f"JURY-{m['mentorIndex']}",
                    "role": "mentor",
                    "mentorIndex": m["mentorIndex"],
                    "password": hashed_pwd,
                    "status": "Approved",
                    "isApproved": True,
                    "approvedBy": "SYSTEM",
                    "approvedAt": now,
                    "isActive": True,
                    "createdAt": now,
                    "updatedAt": now,
                }
                await users.insert_one(doc)
                logger.info("✅ Mentor account (%s) created successfully.", m["email"])
            else:
                await users.update_one(
                    {"_id": existing["_id"]},
                    {
                        "$set": {
                            "fullName": m["fullName"],
                            "role": "mentor",
                            "mentorIndex": m["mentorIndex"],
                            "isApproved": True,
                            "status": "Approved",
                            "isActive": True,
                            "updatedAt": now,
                        }
                    },
                )
    except Exception as e:
        logger.warning("Notice during mentor seeding: %s", e)
