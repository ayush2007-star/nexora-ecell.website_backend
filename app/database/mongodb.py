import logging
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    client: AsyncIOMotorClient = None


mongodb = MongoDB()


async def connect_db():
    """
    Establish asynchronous connection to MongoDB.
    Automatically applies certifi CA bundle when connecting to MongoDB Atlas or TLS-enabled URIs.
    """
    client_kwargs = {
        "maxPoolSize": 50,
        "minPoolSize": 5,
        "serverSelectionTimeoutMS": 5000,
    }

    uri = settings.MONGODB_URI or ""
    if uri.startswith("mongodb+srv://") or "tls=true" in uri.lower() or "ssl=true" in uri.lower():
        client_kwargs["tlsCAFile"] = certifi.where()

    mongodb.client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        **client_kwargs
    )

    try:
        # Verify connection with ping
        await mongodb.client.admin.command("ping")
        logger.info("✅ MongoDB Connected successfully")
    except Exception as e:
        logger.warning(
            "⚠️ MongoDB connection ping warning: %s. "
            "Please ensure MONGODB_URI is correct and IP 0.0.0.0/0 is whitelisted in MongoDB Atlas.",
            e,
        )


async def close_db():
    if mongodb.client:
        mongodb.client.close()
        logger.info("❌ MongoDB Disconnected")


def get_database():
    if mongodb.client is None:
        return None

    return mongodb.client[settings.DATABASE_NAME]