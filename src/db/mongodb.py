from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from src.utils.constants import MONGODB_URI, MONGODB_DB_NAME


class MongoDBManager:
    """
    Manages MongoDB Atlas connection and provides database access.
    """
    _instance: Optional['MongoDBManager'] = None
    _client: Optional[AsyncIOMotorClient] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self):
        """Initialize MongoDB connection."""
        if self._client is None:
            self._client = AsyncIOMotorClient(MONGODB_URI)
            # Verify connection
            await self._client.admin.command('ping')
            print(f"[MongoDB] Connected to database: {MONGODB_DB_NAME}")

    async def close(self):
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            print("[MongoDB] Connection closed")

    @property
    def database(self):
        """Get the database instance."""
        if self._client is None:
            raise Exception("MongoDB client not initialized. Call connect() first.")
        return self._client[MONGODB_DB_NAME]

    @property
    def conversations(self):
        """Get the conversations collection."""
        return self.database.conversations


# Global instance
mongodb = MongoDBManager()
