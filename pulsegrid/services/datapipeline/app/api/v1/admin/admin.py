import json

import structlog
from pydantic import TypeAdapter    #Type Adapter is used to convert into pydantic modelss
from fastapi import APIRouter, Depends, HTTPException, status, Response
import redis.asyncio as redis_asyncio
from pymongo.asynchronous.database import AsyncDatabase


from pulseBot.scrapper import PulseBotScrapper
from core.database import get_database
from pulseBot.crawler import PulseBotCrawler
from schema.source_schema import SourceIds, SourceResponceSchema, SourceSchema, SourceCollection, CrawlObjectSchema
from service.sourceService import SourceService
from api.v1.deps import get_redis_client, get_source_service
from core.logging import setup_logging
from schema.common import ApiResponseSchema

setup_logging()
logger = structlog.get_logger()

router = APIRouter(prefix="/admin", tags=["admin"])
cache_key = "pulsegrid:sources:all"
crawler_cache_key = "pulsegrid:sources:crawl:all"

@router.post("/source", status_code=status.HTTP_201_CREATED,response_model=ApiResponseSchema[SourceIds])
async def create_source(
    source: list[SourceSchema] , # the frontend sends a list of sources
    service: SourceService = Depends(get_source_service),
    redis_client: redis_asyncio.Redis | None = Depends(get_redis_client)
):
    """Create a new source in the database used for data ingestion."""

    newly_created_source = await service.register_new_source(source) #the return of this service will be of like {"inserted-ids": [....,.....,....]}

    await redis_client.delete(cache_key)  #invalidatting the cache since new item has been added into the sources list
    logger.info("made the cache for sources:all expired. since new source has been added into it",)


    return ApiResponseSchema(
        status_code=201,
        message=f"Successfully Created the sources",
        data=newly_created_source
    )


@router.get("/source", response_model=ApiResponseSchema[SourceCollection])
async def get_source(
    service: SourceService = Depends(get_source_service),
    redis_client: redis_asyncio.Redis | None = Depends(get_redis_client)
):
    """Get all sources from the database."""

    
    cached_sources = await redis_client.get(cache_key) if redis_client else None

    if cached_sources:
        logger.info("successfully retrieved the data from cache")
        return Response(content=cached_sources, media_type="application/json")   #Response object uses the starlette's inbuild to directly process the stringified json object (pydantic serialized) into the return format


    sources = await service.get_all_sources()

    serialised_responce = ApiResponseSchema(
        status_code=200,
        message="Successfully retrieved all sources",
        data=SourceCollection(sources=sources)       #SourceCollection expects like ---->    {"sources": [source1, source2, ...]} but  what we get is just a list kike  [source1, source2, ...] therefore wrap the sources with SourceCollection(sources=sources)
    )

    await redis_client.set(cache_key, serialised_responce.model_dump_json()) #.model_dump_json() is used to convert the pydantic serialized responce into stringified json responce so that to save into redis.
    logger.info("successfully set the cached responce")

    return serialised_responce

@router.get("/crawl", response_model=ApiResponseSchema[str])
async def implement_crawler(
    db: AsyncDatabase = Depends(get_database),
    redis_client: redis_asyncio.Redis | None = Depends(get_redis_client)
):
    cached_sources = await redis_client.get(cache_key) if redis_client else None
    
    if not cached_sources:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cached resources not found......."
        )

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
        return ApiResponseSchema(
            status_code=200,
            message=f"Completed the crawl function",
            data='successfully ran the crawler'
        )
    else:
        raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"some sources are not crawlable....."
        )



@router.get("/scrapper", response_model=ApiResponseSchema[str])
async def implement_scrapper(
    db: AsyncDatabase = Depends(get_database),
    redis_client: redis_asyncio.Redis | None = Depends(get_redis_client)
):
    cached_crawl_source = await redis_client.get(crawler_cache_key) if redis_client else None
    
    if not cached_crawl_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cached resources not found......."
        )

    #Initiallzing our crawler bot for crawling
    pulsebot = PulseBotScrapper(
        db = db,
        redis=redis_client,
        concurrency_limit=5,
        max_retries=3,
    )

    parsed_list_of_crawled_objects = await redis_client.lrange(crawler_cache_key, 0, -1) #this converts the stringified responce into python objects -> we want to pass the parsed_source.sources (contains the list of SourceResponceSchema)
    parsed_list_of_crawled_objects_adapter = TypeAdapter(list[CrawlObjectSchema]) #the adapter class to which we have to convert the list of bytes into
    parsed_list_of_crawled_objects_adapter_python_formatted = parsed_list_of_crawled_objects_adapter.validate_python([json.loads(crawl_object_json) for crawl_object_json in parsed_list_of_crawled_objects])

    crawl_responce = await pulsebot.load_the_collection(crawlObjects=parsed_list_of_crawled_objects_adapter_python_formatted)

    if all(crawl_responce):
        return ApiResponseSchema(
            status_code=200,
            message=f"Completed the crawl function",
            data='successfully ran the crawler'
        )
    else:
        raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"some sources are not crawlable....."
        )
