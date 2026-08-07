from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase

from core.database import get_database
from repository.sourceRepository import SourceRepository
from service.sourceService import SourceService

def get_source_service(
    db: AsyncDatabase = Depends(get_database)
) -> SourceService:
    # Instantiate Repository with DB, then pass Repository into Service
    repository = SourceRepository(db)
    return SourceService(repository)
