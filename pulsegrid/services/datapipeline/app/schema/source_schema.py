#this schema file is used to handle the validation and serialization for the source add endpoint which is accessible only by the
# admin
from enum import Enum
from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator, Field, HttpUrl, ConfigDict

class SourceScope(str, Enum):
    TECHNICAL = 'Technical'
    GAMING = 'Gaming'
    CINEMA = 'Cinema'

PyObjectId = Annotated[str, BeforeValidator(str)]

#this will the validator shema for the input data for the source add endpoint
class SourceSchema(BaseModel):
    source_name: str = Field(...)
    source_type: str = Field(...) #can include 'International' or 'National'
    nationality: str | None = Field(None) #will be considered if the type is 'National'
    source_url: HttpUrl = Field(...)
    source_scope: SourceScope

#this is used to serialize the BJSON formatted responce of the source get endpoint
class SourceResponceSchema(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    source_name: str = Field(...)
    source_type: str = Field(...) #can include 'International' or 'National'
    nationality: str | None = Field(None) #will be considered if the type is 'National'
    source_url: HttpUrl = Field(...)
    source_scope: SourceScope

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                        "source_name": "TechCrunch",
                        "source_type": "International",
                        "nationality": "USA",
                        "source_url": "https://techcrunch.com",
                        "source_scope": "TECHNICAL",
                }
        }
    )

#used to serialize the collection of sources returned by the source get endpoint
class SourceCollection(BaseModel):
    sources: list[SourceResponceSchema]
