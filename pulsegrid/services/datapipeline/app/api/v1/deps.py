from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.core.database import get_database
from app.repository.sourceRepository import SourceRepository
from app.service.sourceService import SourceService

def get_source_service(
    db: AsyncDatabase = Depends(get_database)
) -> SourceService:
    # Instantiate Repository with DB, then pass Repository into Service
    repository = SourceRepository(db)
    return SourceService(repository)
