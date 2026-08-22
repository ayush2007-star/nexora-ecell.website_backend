import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.database.collections import get_collections
from app.repositories.scoring_repository import ScoringRepository
from app.repositories.activity_repository import ActivityRepository

logger = logging.getLogger(__name__)

CRITERIA_KEYS = [
    "ideaUsp",
    "targetMarket",
    "growthPotential",
    "revenueModel",
    "stageFuturePlans",
    "teamMembers",
]

CRITERIA_LABELS = {
    "ideaUsp": "Startup Idea and USP",
    "targetMarket": "Target Market and Size",
    "growthPotential": "Growth Potential",
    "revenueModel": "Revenue Model",
    "stageFuturePlans": "Stage of Startup and Future Plans",
    "teamMembers": "Team Members",
}


class ScoringService:
    """
    Business logic for Judge / Mentor evaluations and Leaderboard calculations.
    """

    @staticmethod
    async def get_startups_for_mentor(mentor_id: str) -> Dict[str, Any]:
        collections = get_collections()
        teams_col = collections["teams"]
        projects_col = collections["projects"]
        users_col = collections["users"]

        # Fetch all teams
        teams = await teams_col.find({}).sort("createdAt", -1).to_list(length=None)
        team_ids = [t.get("teamId") for t in teams if t.get("teamId")]
        leader_ids = [t.get("leaderId") for t in teams if t.get("leaderId")]

        projects = await projects_col.find({"teamId": {"$in": team_ids}}).to_list(length=None)
        project_map = {p.get("teamId"): p for p in projects}

        users = await users_col.find({"userId": {"$in": leader_ids}}).to_list(length=None)
        user_map = {u.get("userId"): u for u in users}

        # Fetch scores submitted by this mentor
        mentor_scores = await ScoringRepository.find_scores_by_mentor(mentor_id)
        score_map = {s.get("teamId"): s for s in mentor_scores}

        startups = []
        evaluated_count = 0

        for t in teams:
            team_id = t.get("teamId", "")
            leader = user_map.get(t.get("leaderId", ""), {})
            project = project_map.get(team_id, {})

            score_doc = score_map.get(team_id)
            is_evaluated = score_doc is not None
            if is_evaluated:
                evaluated_count += 1

            startups.append({
                "teamId": team_id,
                "teamName": t.get("teamName") or project.get("projectName") or "Untitled Startup",
                "projectName": project.get("projectName") or t.get("teamName") or "—",
                "eurekaTeamId": project.get("eurekaTeamId") or t.get("eurekaTeamId") or team_id,
                "domain": project.get("domain") or t.get("domain") or "Innovation & Tech",
                "stage": project.get("stage") or "MVP / Prototype",
                "description": project.get("description") or t.get("remarks") or "No description provided.",
                "pitchDeckUrl": project.get("pitchDeckUrl") or "",
                "leaderName": leader.get("fullName") or t.get("leaderName") or "—",
                "leaderEmail": leader.get("email") or "",
                "leaderPhone": leader.get("phone") or "",
                "attendanceStatus": t.get("attendanceStatus", "Absent"),
                "foodStatus": t.get("foodStatus", "Food Pending"),
                "isEvaluated": is_evaluated,
                "myScore": {
                    "scores": score_doc.get("scores") if score_doc else {},
                    "totalScore": score_doc.get("totalScore", 0.0) if score_doc else 0.0,
                    "feedback": score_doc.get("feedback", "") if score_doc else "",
                    "updatedAt": score_doc.get("updatedAt") if score_doc else None,
                } if score_doc else None,
            })

        return {
            "success": True,
            "message": "Startups list loaded for mentor evaluation.",
            "data": startups,
            "metrics": {
                "totalStartups": len(startups),
                "evaluatedCount": evaluated_count,
                "pendingCount": len(startups) - evaluated_count,
            },
        }

    @staticmethod
    async def submit_score(
        team_id: str,
        mentor_user: Dict[str, Any],
        scores_dict: Dict[str, Any],
        feedback: str = "",
    ) -> Dict[str, Any]:
        mentor_id = mentor_user.get("userId") or "MENTOR-01"
        mentor_name = mentor_user.get("fullName") or "Mentor / Judge"
        mentor_index = mentor_user.get("mentorIndex") or 1

        # Strict validation of each criterion (0.0 to 5.0)
        validated_scores = {}
        total_score = 0.0

        for key in CRITERIA_KEYS:
            val = scores_dict.get(key)
            if val is None:
                return {
                    "success": False,
                    "message": f"Missing score for criterion '{CRITERIA_LABELS.get(key, key)}'.",
                }
            try:
                score_num = float(val)
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "message": f"Score for '{CRITERIA_LABELS.get(key, key)}' must be a valid number between 0 and 5.",
                }

            if score_num < 0.0 or score_num > 5.0:
                return {
                    "success": False,
                    "message": f"Score for '{CRITERIA_LABELS.get(key, key)}' must be between 0 and 5 (got {score_num}).",
                }

            validated_scores[key] = round(score_num, 2)
            total_score += score_num

        total_score = round(total_score, 2)

        # Cap total at 30.0
        if total_score > 30.0:
            total_score = 30.0

        saved_doc = await ScoringRepository.upsert_mentor_score(
            team_id=team_id,
            mentor_id=mentor_id,
            mentor_name=mentor_name,
            mentor_index=int(mentor_index),
            scores=validated_scores,
            total_score=total_score,
            feedback=feedback,
        )

        # Log Activity
        try:
            now = datetime.now(timezone.utc)
            await ActivityRepository.create({
                "userId": mentor_id,
                "role": "mentor",
                "action": "MENTOR_SCORE_SUBMIT",
                "module": "Scoring",
                "teamId": team_id,
                "description": f"{mentor_name} submitted evaluation score {total_score}/30 for startup {team_id}.",
                "createdAt": now,
            })
        except Exception as e:
            logger.warning("Activity log error: %s", e)

        return {
            "success": True,
            "message": f"Score saved successfully! ({total_score}/30)",
            "data": saved_doc,
        }

    @staticmethod
    async def get_all_results_leaderboard() -> Dict[str, Any]:
        collections = get_collections()
        teams_col = collections["teams"]
        projects_col = collections["projects"]
        users_col = collections["users"]

        # Fetch all teams
        teams = await teams_col.find({}).to_list(length=None)
        team_ids = [t.get("teamId") for t in teams if t.get("teamId")]
        leader_ids = [t.get("leaderId") for t in teams if t.get("leaderId")]

        projects = await projects_col.find({"teamId": {"$in": team_ids}}).to_list(length=None)
        project_map = {p.get("teamId"): p for p in projects}

        users = await users_col.find({"userId": {"$in": leader_ids}}).to_list(length=None)
        user_map = {u.get("userId"): u for u in users}

        # Fetch all mentor score documents
        all_scores = await ScoringRepository.find_all_scores()

        # Group scores by teamId
        scores_by_team = {}
        for s in all_scores:
            t_id = s.get("teamId")
            if t_id not in scores_by_team:
                scores_by_team[t_id] = {}
            # Map by mentor index or mentorId
            m_idx = s.get("mentorIndex")
            if not m_idx:
                # Try infer from mentorId (e.g. MENTOR-01 -> 1)
                m_id = s.get("mentorId", "")
                if "1" in m_id:
                    m_idx = 1
                elif "2" in m_id:
                    m_idx = 2
                elif "3" in m_id:
                    m_idx = 3
                elif "4" in m_id:
                    m_idx = 4
                else:
                    m_idx = 1
            scores_by_team[t_id][m_idx] = s

        leaderboard = []
        fully_evaluated_count = 0

        for t in teams:
            team_id = t.get("teamId", "")
            leader = user_map.get(t.get("leaderId", ""), {})
            project = project_map.get(team_id, {})

            team_scores = scores_by_team.get(team_id, {})

            m1 = team_scores.get(1)
            m2 = team_scores.get(2)
            m3 = team_scores.get(3)
            m4 = team_scores.get(4)

            submitted_mentors = [m for m in [m1, m2, m3, m4] if m is not None]
            submitted_count = len(submitted_mentors)

            if submitted_count == 4:
                fully_evaluated_count += 1

            combined_total = sum(float(m.get("totalScore", 0.0)) for m in submitted_mentors)
            combined_total = round(combined_total, 2)

            max_possible_current = submitted_count * 30
            average_score = round(combined_total / submitted_count, 2) if submitted_count > 0 else 0.0

            # Percentage calculation
            if submitted_count == 4:
                percentage = round((combined_total / 120.0) * 100, 2)
            elif submitted_count > 0:
                percentage = round((combined_total / (submitted_count * 30.0)) * 100, 2)
            else:
                percentage = 0.0

            leaderboard.append({
                "teamId": team_id,
                "teamName": t.get("teamName") or project.get("projectName") or "Untitled Startup",
                "projectName": project.get("projectName") or t.get("teamName") or "—",
                "eurekaTeamId": project.get("eurekaTeamId") or t.get("eurekaTeamId") or team_id,
                "domain": project.get("domain") or t.get("domain") or "Innovation & Tech",
                "stage": project.get("stage") or "MVP / Prototype",
                "pitchDeckUrl": project.get("pitchDeckUrl") or "",
                "leaderName": leader.get("fullName") or t.get("leaderName") or "—",
                "leaderEmail": leader.get("email") or "",
                "mentor1": {
                    "submitted": m1 is not None,
                    "totalScore": m1.get("totalScore") if m1 else None,
                    "scores": m1.get("scores") if m1 else None,
                    "feedback": m1.get("feedback") if m1 else "",
                    "updatedAt": m1.get("updatedAt") if m1 else None,
                },
                "mentor2": {
                    "submitted": m2 is not None,
                    "totalScore": m2.get("totalScore") if m2 else None,
                    "scores": m2.get("scores") if m2 else None,
                    "feedback": m2.get("feedback") if m2 else "",
                    "updatedAt": m2.get("updatedAt") if m2 else None,
                },
                "mentor3": {
                    "submitted": m3 is not None,
                    "totalScore": m3.get("totalScore") if m3 else None,
                    "scores": m3.get("scores") if m3 else None,
                    "feedback": m3.get("feedback") if m3 else "",
                    "updatedAt": m3.get("updatedAt") if m3 else None,
                },
                "mentor4": {
                    "submitted": m4 is not None,
                    "totalScore": m4.get("totalScore") if m4 else None,
                    "scores": m4.get("scores") if m4 else None,
                    "feedback": m4.get("feedback") if m4 else "",
                    "updatedAt": m4.get("updatedAt") if m4 else None,
                },
                "submittedCount": submitted_count,
                "totalMentors": 4,
                "combinedTotal": combined_total,
                "maxPossibleScore": 120 if submitted_count == 4 else max_possible_current,
                "averageScore": average_score,
                "percentage": percentage,
                "isFullyEvaluated": submitted_count == 4,
                "statusText": f"Completed (4/4)" if submitted_count == 4 else f"Incomplete ({submitted_count}/4 Submitted)" if submitted_count > 0 else "Pending (0/4)",
            })

        # Sort leaderboard descending by combined total, then by average score
        leaderboard.sort(
            key=lambda x: (x["combinedTotal"], x["averageScore"], x["submittedCount"]),
            reverse=True,
        )

        # Assign ranks
        current_rank = 1
        for i, item in enumerate(leaderboard):
            if i > 0:
                prev = leaderboard[i - 1]
                if prev["combinedTotal"] == item["combinedTotal"] and prev["averageScore"] == item["averageScore"]:
                    item["rank"] = prev["rank"]
                else:
                    item["rank"] = i + 1
            else:
                item["rank"] = 1

        return {
            "success": True,
            "message": "Leaderboard loaded successfully.",
            "data": leaderboard,
            "metrics": {
                "totalStartups": len(leaderboard),
                "fullyEvaluatedCount": fully_evaluated_count,
                "pendingEvaluationsCount": len(leaderboard) - fully_evaluated_count,
            },
        }

    @staticmethod
    async def get_startup_detailed_scores(team_id: str) -> Dict[str, Any]:
        collections = get_collections()
        teams_col = collections["teams"]
        projects_col = collections["projects"]
        users_col = collections["users"]

        team = await teams_col.find_one({"teamId": team_id}, {"_id": 0})
        if not team:
            return {
                "success": False,
                "message": "Startup not found.",
            }

        project = await projects_col.find_one({"teamId": team_id}, {"_id": 0})
        leader = await users_col.find_one({"userId": team.get("leaderId")}, {"_id": 0})

        scores = await ScoringRepository.find_scores_by_team(team_id)

        return {
            "success": True,
            "message": "Startup evaluation details fetched.",
            "data": {
                "team": team,
                "project": project,
                "leader": leader,
                "scores": scores,
                "criteriaDefinitions": [
                    {"key": k, "label": CRITERIA_LABELS[k], "maxScore": 5}
                    for k in CRITERIA_KEYS
                ],
            },
        }
