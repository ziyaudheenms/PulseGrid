#this schema file is used to handle the validation and serialization for the source add endpoint which is accessible only by the
# admin
from enum import Enum
from datetime import datetime, timezone

from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator, Field, HttpUrl, ConfigDict

class SourceScope(str, Enum):
    TECHNICAL = 'Technical'
    SPORTS = 'Sports'
    CINEMA = 'Cinema'

PyObjectId = Annotated[str, BeforeValidator(str)]

#this will the validator shema for the input data for the source add endpoint
class SourceSchema(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    source_name: str = Field(...)
    source_type: str = Field(...) #can include 'International' or 'National'
    nationality: str | None = Field(None) #will be considered if the type is 'National'
    source_url: str
    source_scope: SourceScope
    crawl_pattern: str
    #why lambda? -> datetime.now(timezone.utc) takes an argument (timezone.utc), but default_factory requires a callable that takes zero arguments. Using lambda bridges this gap.
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  #timezone.utc is used so in order to get the geographical data along with the timestamp
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

#this is used to serialize the BJSON formatted responce of the source get endpoint
class SourceResponceSchema(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    source_name: str
    source_type: str  #can include 'International' or 'National'
    nationality: str | None = Field(None) #will be considered if the type is 'National'
    source_url: str
    source_scope: SourceScope
    crawl_pattern: str
    created_at: datetime | None = Field(None)
    updated_at: datetime | None = Field(None)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                        "_id": "507f1f77bcf86cd799439011",
                        "source_name": "TechCrunch",
                        "source_type": "International",
                        "nationality": "USA",
                        "source_url": "https://techcrunch.com",
                        "source_scope": "Technical",
                        "crawl_pattern": "https://techcrunch.com/feed/",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z",
                }
        }
    )

#this class is used when creating bulk sources whcih returns there respective ids.
class SourceIds(BaseModel):
    inserted_ids: list[str]



#used to serialize the collection of sources returned by the source get endpoint
class SourceCollection(BaseModel):
    sources: list[SourceResponceSchema]


#used to serialize the collection of the crawled sources with the no of articles to be crawled and there counts.
class CrawlObjectSchema(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    source_id: str
    no_of_urls: int  #can include 'International' or 'National'
    article_urls: list[str] #will contain the list of all the urls that are to be fetched for scrapping.
    created_at: datetime | None = Field(None)
    updated_at: datetime | None = Field(None)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                        "_id": "507f1f77bcf86cd799439012",
                        "source_id": "507f1f77bcf86cd799439011",
                        "no_of_urls": 5,
                        "article_urls": ["https://techcrunch.com/article1", "https://techcrunch.com/article2"],
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z",
                }
        }
    )