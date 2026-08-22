from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from app.database.collections import get_collections


class AttendanceRepository:
    """
    Repository for Attendance and Food distribution status tracking.
    """

    @staticmethod
    async def get_attendance_list(
        search: str = "",
        attendance_filter: str = "",
        food_filter: str = "",
    ) -> Dict[str, Any]:
        collections = get_collections()
        teams_col = collections["teams"]
        users_col = collections["users"]
        projects_col = collections["projects"]
        members_col = collections["members"]

        # Fetch all teams
        cursor = teams_col.find({}).sort("createdAt", -1)
        teams = await cursor.to_list(length=None)

        # Pre-fetch users, projects, and members for efficient mapping
        team_ids = [t.get("teamId") for t in teams if t.get("teamId")]
        leader_ids = [t.get("leaderId") for t in teams if t.get("leaderId")]

        users = await users_col.find({"userId": {"$in": leader_ids}}).to_list(length=None)
        user_map = {u.get("userId"): u for u in users}

        projects = await projects_col.find({"teamId": {"$in": team_ids}}).to_list(length=None)
        project_map = {p.get("teamId"): p for p in projects}

        members = await members_col.find({"teamId": {"$in": team_ids}}).to_list(length=None)
        members_by_team = {}
        for m in members:
            t_id = m.get("teamId")
            if t_id not in members_by_team:
                members_by_team[t_id] = []
            members_by_team[t_id].append({
                "memberId": m.get("memberId"),
                "memberName": m.get("memberName") or m.get("name", ""),
                "memberEmail": m.get("memberEmail") or m.get("email", ""),
                "memberPhone": m.get("memberPhone") or m.get("phone", ""),
                "role": m.get("role", "Member"),
                "isLeader": m.get("isLeader", False),
                "attendanceStatus": m.get("attendanceStatus", "Absent"),
                "foodStatus": m.get("foodStatus", "Food Pending"),
            })

        records = []
        total_present = 0
        total_absent = 0
        total_food_done = 0
        total_food_pending = 0

        search_lower = search.strip().lower()

        for t in teams:
            team_id = t.get("teamId", "")
            leader_id = t.get("leaderId", "")
            leader = user_map.get(leader_id, {})
            project = project_map.get(team_id, {})
            t_members = members_by_team.get(team_id, [])

            att_status = t.get("attendanceStatus") or "Absent"
            food_status = t.get("foodStatus") or "Food Pending"

            # Global counters before filter
            if att_status == "Present":
                total_present += 1
            else:
                total_absent += 1

            if food_status == "Food Done":
                total_food_done += 1
            else:
                total_food_pending += 1

            leader_name = leader.get("fullName") or t.get("leaderName") or "—"
            leader_email = leader.get("email") or t.get("leaderEmail") or ""
            leader_phone = leader.get("phone") or t.get("leaderPhone") or ""
            team_name = t.get("teamName") or project.get("projectName") or "Untitled Team"
            project_name = project.get("projectName") or team_name
            eureka_id = project.get("eurekaTeamId") or t.get("eurekaTeamId") or team_id
            domain = project.get("domain") or t.get("domain") or "General"

            # Check search match
            if search_lower:
                match_search = (
                    search_lower in team_id.lower()
                    or search_lower in str(eureka_id).lower()
                    or search_lower in team_name.lower()
                    or search_lower in project_name.lower()
                    or search_lower in leader_name.lower()
                    or search_lower in leader_email.lower()
                    or search_lower in str(leader_phone).lower()
                )
                if not match_search:
                    continue

            # Check attendance filter
            if attendance_filter:
                if attendance_filter.lower() == "present" and att_status != "Present":
                    continue
                if attendance_filter.lower() == "absent" and att_status == "Present":
                    continue

            # Check food filter
            if food_filter:
                if food_filter.lower() in ["food done", "done"] and food_status != "Food Done":
                    continue
                if food_filter.lower() in ["food pending", "pending"] and food_status == "Food Done":
                    continue

            records.append({
                "teamId": team_id,
                "teamName": team_name,
                "projectName": project_name,
                "eurekaTeamId": eureka_id,
                "leaderName": leader_name,
                "leaderEmail": leader_email,
                "leaderPhone": leader_phone,
                "domain": domain,
                "attendanceStatus": att_status,
                "foodStatus": food_status,
                "attendanceUpdatedAt": t.get("attendanceUpdatedAt"),
                "foodUpdatedAt": t.get("foodUpdatedAt"),
                "members": t_members,
                "createdAt": t.get("createdAt"),
            })

        return {
            "records": records,
            "counts": {
                "total": len(teams),
                "filtered": len(records),
                "totalPresent": total_present,
                "totalAbsent": total_absent,
                "totalFoodDone": total_food_done,
                "totalFoodPending": total_food_pending,
            },
        }

    @staticmethod
    async def update_team_attendance(
        team_id: str,
        status: str,
        updated_by: str = "Admin",
    ) -> bool:
        collections = get_collections()
        teams_col = collections["teams"]
        members_col = collections["members"]
        now = datetime.now(timezone.utc)

        normalized = "Present" if status.lower() == "present" else "Absent"

        result = await teams_col.update_one(
            {"teamId": team_id},
            {
                "$set": {
                    "attendanceStatus": normalized,
                    "attendanceUpdatedAt": now,
                    "attendanceMarkedBy": updated_by,
                }
            }
        )

        # Also update leader/members attendance if marked present
        await members_col.update_many(
            {"teamId": team_id},
            {
                "$set": {
                    "attendanceStatus": normalized,
                    "attendanceUpdatedAt": now,
                }
            }
        )

        return result.modified_count > 0 or result.matched_count > 0

    @staticmethod
    async def update_team_food(
        team_id: str,
        status: str,
        updated_by: str = "Admin",
    ) -> bool:
        collections = get_collections()
        teams_col = collections["teams"]
        members_col = collections["members"]
        now = datetime.now(timezone.utc)

        normalized = "Food Done" if "done" in status.lower() else "Food Pending"

        result = await teams_col.update_one(
            {"teamId": team_id},
            {
                "$set": {
                    "foodStatus": normalized,
                    "foodUpdatedAt": now,
                    "foodMarkedBy": updated_by,
                }
            }
        )

        await members_col.update_many(
            {"teamId": team_id},
            {
                "$set": {
                    "foodStatus": normalized,
                    "foodUpdatedAt": now,
                }
            }
        )

        return result.modified_count > 0 or result.matched_count > 0

    @staticmethod
    async def update_member_attendance(
        team_id: str,
        member_id: str,
        status: str,
    ) -> bool:
        collections = get_collections()
        members_col = collections["members"]
        now = datetime.now(timezone.utc)

        normalized = "Present" if status.lower() == "present" else "Absent"

        result = await members_col.update_one(
            {"teamId": team_id, "memberId": member_id},
            {
                "$set": {
                    "attendanceStatus": normalized,
                    "attendanceUpdatedAt": now,
                }
            }
        )
        return result.modified_count > 0 or result.matched_count > 0

    @staticmethod
    async def update_member_food(
        team_id: str,
        member_id: str,
        status: str,
    ) -> bool:
        collections = get_collections()
        members_col = collections["members"]
        now = datetime.now(timezone.utc)

        normalized = "Food Done" if "done" in status.lower() else "Food Pending"

        result = await members_col.update_one(
            {"teamId": team_id, "memberId": member_id},
            {
                "$set": {
                    "foodStatus": normalized,
                    "foodUpdatedAt": now,
                }
            }
        )
        return result.modified_count > 0 or result.matched_count > 0
