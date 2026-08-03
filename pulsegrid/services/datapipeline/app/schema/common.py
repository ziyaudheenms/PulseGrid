from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponseSchema(BaseModel, Generic[T]):   #Generic[T] -> is used to make that particular data field accept any kind of the data type that is comming it to it, we can also mwntion the kind of generic data we need.
    status_code: int
    message: str
    data: T | None = None
