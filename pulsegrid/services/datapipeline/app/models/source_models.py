from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class SourceScope(str, Enum):
    TECHNICAL = 'Technical'
    GAMING = 'Gaming'
    CINEMA = 'Cinema'

class SourceModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    source_name: str = Field(...)
    source_type: str = Field(...) #can include 'International' or 'National'
    nationality: str | None = Field(None) #will be considered if the type is 'National'
    source_url: HttpUrl = Field(...)
    source_scope: SourceScope

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
