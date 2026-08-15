import structlog
from fastapi import APIRouter, Depends, status, Response
import redis.asyncio as redis_asyncio

from schema.source_schema import SourceIds, SourceResponceSchema, SourceSchema, SourceCollection
from service.sourceService import SourceService
from api.v1.deps import get_redis_client, get_source_service
from core.logging import setup_logging
from schema.common import ApiResponseSchema

setup_logging()
logger = structlog.get_logger()

router = APIRouter(prefix="/admin", tags=["admin"])
cache_key = "pulsegrid:sources:all"

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

    
