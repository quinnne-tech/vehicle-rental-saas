"""MongoDB Connection Management"""

from motor.motor_asyncio import AsyncClient, AsyncDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Global database instance
db: AsyncDatabase = None


async def connect_to_mongo():
    """Establish MongoDB connection"""
    global db
    try:
        client = AsyncClient(settings.MONGODB_URI)
        # Test connection
        await client.admin.command("ping")
        db = client[settings.MONGODB_DB]
        logger.info("✅ Successfully connected to MongoDB")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection"""
    global db
    if db:
        db.client.close()
        logger.info("✅ MongoDB connection closed")


def get_db() -> AsyncDatabase:
    """Get database instance"""
    if db is None:
        raise RuntimeError("Database not connected")
    return db
