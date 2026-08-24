"""
Used to initiate the tasks that is needed for the initially face of data pipeline

    - Used to route to the respected function
    - Triggers the data Crawl
    - Triggers the data Scrap

    Architecture
        - The fucntion that has to route the task and the end function that is to be processed to full the task both 
          should contain the parameter job: Job this contains the name of the function to be triggered and the data payload
          in the json format

          eg:-
                def hello(job:Job):
                    name=job.name #gives the name used when the task was pushed into the queue


    KEY PROBLEM HERE
                - Inintially I functions was running through the http cycle and I was able to use the dependency Injection,
                  here we can inject the dependencies in the background workers , we have to open an saperated and isolated connections 
                  with this environment to work with that.

"""

import json
import os
from typing import Any

from pydantic import TypeAdapter
import structlog
import redis.asyncio as redis_asyncio
from bullmq import Job

from pulseBot.scrapper import PulseBotScrapper
from schema.common import ApiResponseSchema
from schema.source_schema import CrawlObjectSchema, SourceCollection
from pulseBot.crawler import PulseBotCrawler
from api.deps import get_redis_client
from core.database import get_database
from core.config import settings
from core.logging import setup_logging

setup_logging()
logger = structlog.get_logger()

async def implement_crawler_handler(job:Job):

    db = await get_database()
    redis_client = redis_asyncio.from_url(url=os.getenv("DATAPIPELINE_REDIS_TCP_URL") or '', password=os.getenv("DATAPIPELINE_REDIS_REST_TOKEN") or '')

    try:
        cached_sources = await redis_client.get(settings.cache_key) if redis_client else None
        
        if not cached_sources:
            logger.error("The sources have not being cached......")
            return
        
        #Initiallzing our crawler bot for crawling
        pulsebot = PulseBotCrawler(
            db = db,
            redis=redis_client,
            concurrency_limit=5,
            max_retries=3,
        )

        parsed_sources = ApiResponseSchema[SourceCollection].model_validate_json(cached_sources)  #this converts the stringified responce into python objects -> we want to pass the parsed_source.sources (contains the list of SourceResponceSchema)
        

        crawl_responce = await pulsebot.fetch_urls(parsed_sources.data.sources)

        if all(crawl_responce):
            logger.info("Completed the Crawling of the sources successfully", status = crawl_responce)
        else:
            logger.info("Completed the Crawling of the sources Partially! Some sources havent able to complete the crawling", status = crawl_responce)
    finally:
        #once all the process completed either successfull or failure cleanig up the openened connections
        await redis_client.close()
        await db.client.close()



async def implement_scrapper_handler(job:Job):

    db = await get_database()
    redis_client = redis_asyncio.from_url(url=os.getenv("DATAPIPELINE_REDIS_TCP_URL") or '', password=os.getenv("DATAPIPELINE_REDIS_REST_TOKEN") or '')

    try:

        cached_crawl_objects = await redis_client.lrange(settings.crawler_cache_key, 0, -1) #this converts the stringified responce into python objects -> we want to pass the parsed_source.sources (contains the list of SourceResponceSchema)

        
        if not cached_crawl_objects:
            logger.error("The crawled articles arent being cached......")
            return

        cached_crawl_objects = cached_crawl_objects[1:] #the first element in the redis array is b'value' since we dont need that just eliminating the first element out 

        # Initiallzing our crawler bot for crawling
        pulsebot = PulseBotScrapper(
            db = db,
            redis=redis_client,
            concurrency_limit=5,
            max_retries=3,
        )

        parsed_list_of_crawled_objects_adapter = TypeAdapter(list[CrawlObjectSchema]) #the adapter class to which we have to convert the list of bytes into
        parsed_list_of_crawled_objects_adapter_python_formatted = parsed_list_of_crawled_objects_adapter.validate_python([json.loads(crawl_object_json) for crawl_object_json in cached_crawl_objects])

        crawl_responce = await pulsebot.load_the_collection(crawlObjects=parsed_list_of_crawled_objects_adapter_python_formatted)

        if all(crawl_responce):
            logger.info("Completed the scrapping of the articles successfully", status = crawl_responce)
        else:
            logger.info("Completed the scrapping of the articles Partially! Some articles havent able to complete the scrapping", status = crawl_responce)

    finally:
        #once all the process completed either successfull or failure cleanig up the openened connections
        await redis_client.close()
        await db.client.close()
            
            
async def route_data_fetch_task(job:Job, token:str) -> Any:
    """
    Routes to the respected function that is the task which is to be performed by the Worker
    """
    logger.info("Got a task, looking for the function suitable to execute this.")

    if job.name == "implement_crawler":
        return await implement_crawler_handler(job)
    elif job.name == "implement_scrapper":
        return await implement_scrapper_handler(job)