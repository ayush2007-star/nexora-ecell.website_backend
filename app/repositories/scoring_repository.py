from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from app.database.collections import get_collections


class ScoringRepository:
    """
    Repository for Mentor and Judge evaluations stored in mentor_scores collection.
    """

    @staticmethod
    async def upsert_mentor_score(
        team_id: str,
        mentor_id: str,
        mentor_name: str,
        mentor_index: int,
        scores: Dict[str, float],
        total_score: float,
        feedback: str = "",
    ) -> Dict[str, Any]:
        collections = get_collections()
        scores_col = collections.get("mentor_scores")
        if scores_col is None:
            raise Exception("mentor_scores collection not initialized.")

        now = datetime.now(timezone.utc)

        doc = {
            "teamId": team_id,
            "mentorId": mentor_id,
            "mentorName": mentor_name,
            "mentorIndex": mentor_index,
            "scores": scores,
            "totalScore": round(float(total_score), 2),
            "feedback": feedback.strip() if feedback else "",
            "updatedAt": now,
        }

        await scores_col.update_one(
            {"teamId": team_id, "mentorId": mentor_id},
            {
                "$set": doc,
                "$setOnInsert": {
                    "createdAt": now,
                    "scoreId": f"SCR-{mentor_id}-{team_id}",
                },
            },
            upsert=True,
        )

        return await scores_col.find_one(
            {"teamId": team_id, "mentorId": mentor_id},
            {"_id": 0},
        )

    @staticmethod
    async def find_score(team_id: str, mentor_id: str) -> Optional[Dict[str, Any]]:
        collections = get_collections()
        scores_col = collections.get("mentor_scores")
        if scores_col is None:
            return None

        return await scores_col.find_one(
            {"teamId": team_id, "mentorId": mentor_id},
            {"_id": 0},
        )

    @staticmethod
    async def find_scores_by_team(team_id: str) -> List[Dict[str, Any]]:
        collections = get_collections()
        scores_col = collections.get("mentor_scores")
        if scores_col is None:
            return []

        cursor = scores_col.find({"teamId": team_id}, {"_id": 0}).sort("mentorIndex", 1)
        return await cursor.to_list(length=None)

    @staticmethod
    async def find_scores_by_mentor(mentor_id: str) -> List[Dict[str, Any]]:
        collections = get_collections()
        scores_col = collections.get("mentor_scores")
        if scores_col is None:
            return []

        cursor = scores_col.find({"mentorId": mentor_id}, {"_id": 0})
        return await cursor.to_list(length=None)

    @staticmethod
    async def find_all_scores() -> List[Dict[str, Any]]:
        collections = get_collections()
        scores_col = collections.get("mentor_scores")
        if scores_col is None:
            return []

        cursor = scores_col.find({}, {"_id": 0})
        return await cursor.to_list(length=None)
