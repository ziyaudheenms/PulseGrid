from fastapi import HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase
from schema.source_schema import SourceSchema

class SourceRepository:
    def __init__(self, db: AsyncDatabase):
        self.collection = db["source"]  #Collection inside the database where these documents are stored

    async def create_source(self, source_data: list[dict]) -> dict:
        result = await self.collection.insert_many(source_data)
        return {"inserted_ids": [str(id) for id in result.inserted_ids]}

    async def get_by_name(self, name: str) -> dict | None:
        document =  await self.collection.find_one({"source_name": name})
        return document

    async def get_by_name_of_array(self, names: list[str]) -> list | None:
        documents =  await self.collection.find({"source_name": {"$in": names}}).to_list(length=None)  # $in operator is used to match any of the names in the list
        return documents

    async def get_all_sources(self) -> list:
        return await self.collection.find().to_list(length=None)
