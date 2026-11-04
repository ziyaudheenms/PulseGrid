from typing import Any
import structlog
from bullmq import Job

from pulseClean.embedEngine import PulseCleanEmbedd

from core.database import get_database
from core.config import settings
from core.logging import setup_logging

setup_logging()
logger = structlog.get_logger()

async def implement_embedding_handler(job:Job):
    logger.info(f"Got a task, looking for the function suitable to execute this. Job name: {job.name}")
    db = await get_database()

    try:

        #Initiallzing our embedd bot for initializing the embedding
        pulseclean = PulseCleanEmbedd(
            db = db,
            concurrency_limit=5,
            max_retries=3,
            transformer_model='sentence-transformers/all-MiniLM-L6-v2'
        )

        #all the required batching , processing asyn, controlling the simultaneous async threads all are controlled by the PulseCleanClass itself
        #we just have to initiate push for the batching process
        logger.info("Starting the embedding process for the articles in the database")
        await pulseclean.fetch_article_batch(batch_size=50)
    finally:
        #once all the process completed either successfull or failure cleanig up the openened connections
        # await db.client.close()
        pass


async def implement_classification_handler(job:Job):
    pass