import os
import structlog

from dotenv import load_dotenv
from pymongo import AsyncMongoClient  #adaptor that is used to connect to MongoDB asynchronously

from core.config import settings

logger = structlog.get_logger()


class Database:
    client: AsyncMongoClient | None = None

database = Database()

#used to connect to the MongoDB database asynchronously
async def connect_to_mongo():
    database.client = AsyncMongoClient(settings.DATABASE_URL)
    logger.info("Connected to MongoDB", url=settings.DATABASE_URL, db_name=settings.DATABASE_NAME)

#used to disconnect from the MongoDB database asynchronously
async def disconnect_from_mongo():
    if database.client:
        await database.client.close()
        logger.info("Disconnected from MongoDB", url=settings.DATABASE_URL, db_name=settings.DATABASE_NAME)

#used to get the database instance asynchronously
async def get_database():
    if database.client:
        return database.client[settings.DATABASE_NAME]
    else:
        logger.error("Could not find the database client", url=settings.DATABASE_URL, db_name=settings.DATABASE_NAME)