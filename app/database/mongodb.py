from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


class MongoDB:

    client: AsyncIOMotorClient = None


mongodb = MongoDB()


async def connect_db():

    mongodb.client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        maxPoolSize=50,
        minPoolSize=5,
        serverSelectionTimeoutMS=5000
    )

    print("✅ MongoDB Connected")


async def close_db():

    if mongodb.client:
        mongodb.client.close()
        print("❌ MongoDB Disconnected")


def get_database():

    if mongodb.client is None:
        return None

    return mongodb.client[settings.DATABASE_NAME]