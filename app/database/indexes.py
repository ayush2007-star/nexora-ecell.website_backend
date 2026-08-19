import logging
from app.database.collections import get_collections

logger = logging.getLogger(__name__)


async def create_indexes():
    collections = get_collections()

    users = collections.get("users")
    teams = collections.get("teams")
    projects = collections.get("projects")
    certificates = collections.get("certificates")

    if users is None or teams is None or projects is None or certificates is None:
        logger.warning("Database collections unavailable: skipping index creation.")
        return

    try:
        await users.create_index("email", unique=True, sparse=True)
        await users.create_index("phone", sparse=True)
        await teams.create_index("teamId", unique=True)
        await projects.create_index("projectId", unique=True, sparse=True)
        await certificates.create_index("certificateId", unique=True)
        logger.info("✅ Database Indexes Created successfully.")
    except Exception as e:
        logger.warning("Index creation notice: %s", e)
