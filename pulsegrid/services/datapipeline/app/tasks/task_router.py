"""
This module is used to handle the routing of the tasks with the datapipeline task manager powered with bullmq


"""
from typing import Any

import structlog
from bullmq import Job

from tasks.cleaning import (
    implement_clickbait_handler,
    implement_embedding_handler,
    implement_classification_handler,
)
from core.logging import setup_logging
from tasks.data_fetch import implement_crawler_handler, implement_scrapper_handler


setup_logging()
logger = structlog.get_logger()


async def route_fetch_task(job:Job, token:str) -> Any:
    """
    Routes to the respected function that is the task which is to be performed by the Worker
    """
    logger.info(f"Got a task, looking for the function suitable to execute this. Job name: {job.name}")


    if job.name == "implement_crawler":
        logger.info("MATCHED: implement_crawler", job_name=job.name)
        return await implement_crawler_handler(job)
    elif job.name == "implement_scrapper":
        logger.info("MATCHED: implement_scrapper", job_name=job.name)
        return await implement_scrapper_handler(job)
    elif job.name == "implement_embedding":
        logger.info("MATCHED: implement_embedding", job_name=job.name)
        return await implement_embedding_handler(job)
    elif job.name == "implement_classification":
            logger.info("MATCHED: implement_classification", job_name=job.name)
            return await implement_classification_handler(job)
    elif job.name == "implement_clickbait":
        logger.info("MATCHED: implement_clickbait", job_name=job.name)
        return await implement_clickbait_handler(job)