from fastapi import HTTPException, status
from repository.sourceRepository import SourceRepository
from schema.source_schema import SourceSchema

class SourceService:
    def __init__(self, repository: SourceRepository):
        self.repository = repository

    async def register_new_source(self, source: SourceSchema) -> dict:
        # Business logic validation
        existing_source = await self.repository.get_by_name(source.source_name)
        if existing_source:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source with name '{source.source_name}' already exists."
            )

        # Convert Pydantic model to dictionary
        source_dict = source.model_dump(by_alias=True)

        # Save via repository
        return await self.repository.create_source(source_dict)

    async def get_all_sources(self) -> list:
        return await self.repository.get_all_sources()
