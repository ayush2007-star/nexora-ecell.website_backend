from app.database.collections import get_collections


async def create_indexes():

    collections = get_collections()

    users = collections["users"]
    teams = collections["teams"]
    projects = collections["projects"]
    certificates = collections["certificates"]

    await users.create_index("email", unique=True)
    await users.create_index("phone", unique=True)

    await teams.create_index("teamId", unique=True)

    await projects.create_index("projectId", unique=True)

    await certificates.create_index(
        "certificateId",
        unique=True
    )

    print("✅ Database Indexes Created")
