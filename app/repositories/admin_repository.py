from app.database.collections import get_collections


class AdminRepository:

    @staticmethod
    async def dashboard():
        collections = get_collections()

        users = collections["users"]
        teams = collections["teams"]
        projects = collections["projects"]

        return {
            "totalUsers": await users.count_documents({}),
            "totalTeams": await teams.count_documents({}),
            "pendingTeams": await teams.count_documents({"status": "Pending"}),
            "approvedTeams": await teams.count_documents({"status": "Approved"}),
            "rejectedTeams": await teams.count_documents({"status": "Rejected"}),
            "totalProjects": await projects.count_documents({})
        }

    @staticmethod
    async def dashboard_stats():
        teams_collection = get_collections()["teams"]
        projects_collection = get_collections()["projects"]
        users_collection = get_collections()["users"]

        total_registrations = await teams_collection.count_documents({})

        pending = await teams_collection.count_documents(
            {"status": "Pending"}
        )

        approved = await teams_collection.count_documents(
            {"status": "Approved"}
        )

        rejected = await teams_collection.count_documents(
            {"status": "Rejected"}
        )

        total_projects = await projects_collection.count_documents({})

        colleges = await users_collection.distinct("college")

        students = await users_collection.count_documents({})

        return {
            "totalRegistrations": total_registrations,
            "pendingRegistrations": pending,
            "approvedRegistrations": approved,
            "rejectedRegistrations": rejected,
            "totalProjects": total_projects,
            "totalColleges": len(colleges),
            "totalStudents": students
        }

    @staticmethod
    async def registration_list():
        teams_collection = get_collections()["teams"]

        cursor = teams_collection.find(
            {},
            {"_id": 0}
        ).sort(
            "createdAt",
            -1
        )

        return await cursor.to_list(length=None)

    @staticmethod
    async def get_all_registrations(
        page: int = 1,
        limit: int = 10,
        search: str = "",
        status: str = ""
    ):
        collections = get_collections()
        teams = collections["teams"]

        match_stage = {}

        if status:
            match_stage["status"] = status

        if search:
            regex_search = {"$regex": search.strip(), "$options": "i"}
            match_stage["$or"] = [
                {"teamName": regex_search},
                {"teamId": regex_search},
                {"leaderId": regex_search},
            ]

        pipeline = [
            {"$match": match_stage},
            {"$sort": {"createdAt": -1}},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "leaderId",
                    "foreignField": "userId",
                    "as": "leaderDoc"
                }
            },
            {
                "$lookup": {
                    "from": "projects",
                    "localField": "teamId",
                    "foreignField": "teamId",
                    "as": "projectDoc"
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "teamId": 1,
                    "teamName": 1,
                    "leaderId": 1,
                    "status": 1,
                    "remarks": 1,
                    "createdAt": 1,
                    "leaderName": {"$arrayElemAt": ["$leaderDoc.fullName", 0]},
                    "leaderEmail": {"$arrayElemAt": ["$leaderDoc.email", 0]},
                    "leaderPhone": {"$arrayElemAt": ["$leaderDoc.phone", 0]},
                    "projectName": {
                        "$ifNull": [
                            {"$arrayElemAt": ["$projectDoc.projectName", 0]},
                            "$teamName"
                        ]
                    },
                    "domain": {"$arrayElemAt": ["$projectDoc.domain", 0]}
                }
            }
        ]

        # Total count
        total = await teams.count_documents(match_stage)

        # Pagination stages
        paginated_pipeline = pipeline + [
            {"$skip": (page - 1) * limit},
            {"$limit": limit}
        ]

        cursor = teams.aggregate(paginated_pipeline)
        data = await cursor.to_list(length=limit)

        return {
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": (total + limit - 1) // limit if total > 0 else 1
            }
        }

    @staticmethod
    async def registration_details(team_id: str):
        collections = get_collections()

        teams = collections["teams"]
        users = collections["users"]
        members = collections["members"]
        projects = collections["projects"]

        team = await teams.find_one(
            {"teamId": team_id},
            {"_id": 0}
        )

        if not team:
            return None

        leader = await users.find_one(
            {"userId": team["leaderId"]},
            {"_id": 0}
        )

        project = await projects.find_one(
            {"teamId": team_id},
            {"_id": 0}
        )

        team_members = await members.find(
            {"teamId": team_id},
            {"_id": 0}
        ).to_list(length=None)

        return {
            "team": team,
            "leader": leader,
            "project": project,
            "members": team_members
        }

    @staticmethod
    async def approve(team_id):
        collections = get_collections()
        teams = collections["teams"]

        return await teams.update_one(
            {"teamId": team_id},
            {
                "$set": {
                    "status": "Approved"
                }
            }
        )

    @staticmethod
    async def reject(team_id, remarks):
        collections = get_collections()
        teams = collections["teams"]

        return await teams.update_one(
            {"teamId": team_id},
            {
                "$set": {
                    "status": "Rejected",
                    "remarks": remarks
                }
            }
        )
