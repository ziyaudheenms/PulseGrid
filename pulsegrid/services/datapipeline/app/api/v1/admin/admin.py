from fastapi import APIRouter, Depends, status
from app.schema.source_schema import SourceResponceSchema, SourceSchema
from app.service.sourceService import SourceService
from app.api.v1.deps import get_source_service
from app.schema.common import ApiResponseSchema

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/source", status_code=status.HTTP_201_CREATED,response_model=ApiResponseSchema[SourceResponceSchema])
async def create_source(
    source: SourceSchema,
    service: SourceService = Depends(get_source_service)
):
    """Create a new source in the database used for data ingestion."""
    newly_created_source = await service.register_new_source(source)
    return ApiResponseSchema(
        status_code=201,
        message=f"Successfully Created the source {source.source_name}",
        data=newly_created_source
    )
