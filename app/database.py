from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

# Global database instance
client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    # Create indexes
    await create_indexes()
    print("Connected to MongoDB")


async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")


async def create_indexes():
    """Create necessary database indexes"""
    # Users collection
    await db["users"].create_index("email", unique=True)

    # Events collection
    await db["events"].create_index("created_by")

    # Registrations collection
    await db["registrations"].create_index("user_id")
    await db["registrations"].create_index("event_id")
    await db["registrations"].create_index(
        [("user_id", 1), ("event_id", 1)], unique=True
    )


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db
