from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from app.database.collections import get_collections
from app.core.security import hash_password


class MentorRepository:
    """
    Repository layer for Judge / Mentor account operations in MongoDB.
    """

    @staticmethod
    async def get_all_mentors() -> List[Dict[str, Any]]:
        collections = get_collections()
        users_col = collections.get("users")
        scores_col = collections.get("mentor_scores")
        if users_col is None:
            return []

        cursor = users_col.find({"role": "mentor"}, {"_id": 0, "password": 0}).sort("mentorIndex", 1)
        mentors = await cursor.to_list(length=None)

        # Count scored startups per mentor
        for m in mentors:
            user_id = m.get("userId")
            m_idx = m.get("mentorIndex", 1)
            count = 0
            if scores_col is not None:
                count = await scores_col.count_documents({
                    "$or": [{"mentorId": user_id}, {"mentorIndex": m_idx}]
                })
            m["evaluatedStartupsCount"] = count

        return mentors

    @staticmethod
    async def find_mentor_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        collections = get_collections()
        users_col = collections.get("users")
        if users_col is None:
            return None

        return await users_col.find_one({"userId": user_id, "role": "mentor"}, {"_id": 0})

    @staticmethod
    async def find_mentor_by_email(email: str) -> Optional[Dict[str, Any]]:
        collections = get_collections()
        users_col = collections.get("users")
        if users_col is None:
            return None

        return await users_col.find_one({"email": email.strip().lower()}, {"_id": 0})

    @staticmethod
    async def create_mentor(data: Dict[str, Any]) -> Dict[str, Any]:
        collections = get_collections()
        users_col = collections.get("users")
        if users_col is None:
            raise Exception("Users collection unavailable.")

        now = datetime.now(timezone.utc)
        mentor_index = int(data.get("mentorIndex", 1))
        user_id = data.get("userId") or f"MENTOR-0{mentor_index}" if mentor_index < 10 else f"MENTOR-{mentor_index}"

        # If user_id already exists, make unique
        existing = await users_col.find_one({"userId": user_id})
        if existing:
            user_id = f"MENTOR-{datetime.now().strftime('%M%S')}"

        doc = {
            "userId": user_id,
            "fullName": data["fullName"].strip(),
            "email": data["email"].strip().lower(),
            "password": hash_password(data["password"]),
            "phone": data.get("phone", "9876543210"),
            "college": "Nexora Jury Panel",
            "department": data.get("specialization", "Jury & Mentorship"),
            "year": "Judge",
            "rollNumber": f"JURY-{mentor_index}",
            "role": "mentor",
            "mentorIndex": mentor_index,
            "status": "Approved",
            "isApproved": True,
            "approvedBy": "ADMIN",
            "approvedAt": now,
            "isActive": True,
            "createdAt": now,
            "updatedAt": now,
        }

        await users_col.insert_one(doc)

        return await users_col.find_one({"userId": user_id}, {"_id": 0, "password": 0})

    @staticmethod
    async def update_mentor(user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        collections = get_collections()
        users_col = collections.get("users")
        if users_col is None:
            return None

        now = datetime.now(timezone.utc)
        update_fields: Dict[str, Any] = {"updatedAt": now}

        if "fullName" in data and data["fullName"]:
            update_fields["fullName"] = data["fullName"].strip()
        if "email" in data and data["email"]:
            update_fields["email"] = data["email"].strip().lower()
        if "password" in data and data["password"]:
            update_fields["password"] = hash_password(data["password"])
        if "mentorIndex" in data and data["mentorIndex"] is not None:
            update_fields["mentorIndex"] = int(data["mentorIndex"])
            update_fields["rollNumber"] = f"JURY-{data['mentorIndex']}"
        if "specialization" in data and data["specialization"]:
            update_fields["department"] = data["specialization"].strip()
        if "phone" in data and data["phone"]:
            update_fields["phone"] = data["phone"].strip()
        if "isActive" in data and data["isActive"] is not None:
            update_fields["isActive"] = bool(data["isActive"])

        await users_col.update_one({"userId": user_id, "role": "mentor"}, {"$set": update_fields})

        return await users_col.find_one({"userId": user_id}, {"_id": 0, "password": 0})

    @staticmethod
    async def delete_mentor(user_id: str) -> bool:
        collections = get_collections()
        users_col = collections.get("users")
        if users_col is None:
            return False

        res = await users_col.delete_one({"userId": user_id, "role": "mentor"})
        return res.deleted_count > 0
