from fastapi import APIRouter, Depends, status, Form
from schema.source_schema import SourceResponceSchema, SourceSchema, SourceCollection
from service.sourceService import SourceService
from api.v1.deps import get_source_service
from schema.common import ApiResponseSchema

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/source", status_code=status.HTTP_201_CREATED,response_model=ApiResponseSchema[SourceResponceSchema])
async def create_source(
    source: SourceSchema = Form(...),
    service: SourceService = Depends(get_source_service)
):
    """Create a new source in the database used for data ingestion."""
    newly_created_source = await service.register_new_source(source)
    return ApiResponseSchema(
        status_code=201,
        message=f"Successfully Created the source {source.source_name}",
        data=newly_created_source
    )

@router.get("/source", response_model=ApiResponseSchema[SourceCollection])
async def get_source(
    service: SourceService = Depends(get_source_service)
):
    """Get all sources from the database."""
    sources = await service.get_all_sources()
    return ApiResponseSchema(
        status_code=200,
        message="Successfully retrieved all sources",
        data=SourceCollection(sources=sources)       #SourceCollection expects like ---->    {"sources": [source1, source2, ...]} but  what we get is just a list kike  [source1, source2, ...] therefore wrap the sources with SourceCollection(sources=sources)
    )
