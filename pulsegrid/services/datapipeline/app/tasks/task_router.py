"""
This module is used to handle the routing of the tasks with the datapipeline task manager powered with bullmq


"""
from typing import Any

import structlog
from bullmq import Job

from tasks.cleaning import implement_embedding_handler
from core.logging import setup_logging
from tasks.data_fetch import implement_crawler_handler, implement_scrapper_handler


setup_logging()
logger = structlog.get_logger()


async def route_data_fetch_task(job:Job, token:str) -> Any:
    """
    Routes to the respected function that is the task which is to be performed by the Worker
    """
    logger.info("Got a task, looking for the function suitable to execute this.")

    if job.name == "implement_crawler":
        return await implement_crawler_handler(job)
    elif job.name == "implement_scrapper":
        return await implement_scrapper_handler(job)
    elif job.name == "implement_embedding":
            return await implement_embedding_handler(job)