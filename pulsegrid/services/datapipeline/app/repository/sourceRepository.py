from fastapi import HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase
from schema.source_schema import SourceSchema

class SourceRepository:
    def __init__(self, db: AsyncDatabase):
        self.collection = db["source"]  #Collection inside the database where these documents are stored

    async def create_source(self, source_data: dict) -> dict:
        result = await self.collection.insert_one(source_data)
        source_data["_id"] = str(result.inserted_id)
        return source_data

    async def get_by_name(self, name: str) -> dict | None:
        document =  await self.collection.find_one({"source_name": name})
        return document

    async def get_all_sources(self) -> list:
        return await self.collection.find().to_list(length=None)
