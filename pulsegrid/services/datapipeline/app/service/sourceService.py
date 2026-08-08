from pydantic import TypeAdapter
from fastapi import HTTPException, status
from repository.sourceRepository import SourceRepository
from schema.source_schema import SourceSchema

class SourceService:
    def __init__(self, repository: SourceRepository):
        self.repository = repository

    async def register_new_source(self, source: list[SourceSchema]) -> dict:
        # Business logic validation
        names = [s.source_name for s in source]
        existing_source = await self.repository.get_by_name_of_array(names)  # Check if any of the sources already exist if so returns the documents

        if existing_source:
            existing_names = [s["source_name"] for s in existing_source]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source with names '{existing_names}' already exists."
            )

        # Convert Pydantic model to dictionary Type Adapter is used to convert all the array of python objects into a list of dictionaries.
        adapter = TypeAdapter(list[SourceSchema])
        source_dict = adapter.dump_python(source)

        # Save via repository
        return await self.repository.create_source(source_dict)

    async def get_all_sources(self) -> list:
        return await self.repository.get_all_sources()
