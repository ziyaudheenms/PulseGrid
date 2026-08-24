
import structlog
from fastapi import Depends, Request
from pymongo.asynchronous.database import AsyncDatabase
import redis.asyncio as redis_asyncio
from bullmq import Queue

from core.queue import get_queue
from core.logging import setup_logging
from core.database import get_database
from repository.sourceRepository import SourceRepository
from service.sourceService import SourceService


setup_logging()
logger = structlog.get_logger()


def get_source_service(
    db: AsyncDatabase = Depends(get_database)
) -> SourceService:
    # Instantiate Repository with DB, then pass Repository into Service
    repository = SourceRepository(db)
    return SourceService(repository)


def get_redis_client(
        request: Request 
) -> redis_asyncio.Redis | None:

    if request.app.state.redis is None:
        logger.error("Redis client is not initialized.")
        return None  # or raise an exception, depending on your error handling strategy

    return request.app.state.redis

def get_the_respected_queue(name:str) -> Queue:
    
    return get_queue(name)