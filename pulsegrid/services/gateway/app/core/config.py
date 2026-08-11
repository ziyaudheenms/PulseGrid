from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "PulseGrid API Gateway"
    VERSION: str = "1.0.0"

    # Microservice Target URLs and Respected Versions
    DATAPIPELINE_SERVICE_URL: str = "http://localhost:8000"
    DATAPIPELINE_VERSION: str = "v1"


    #Authentication parameters for clerk based SDK
    # clerk_secret_key: str
    CLERK_SECRET_KEY: str | None = 'sk_test_XeVlBYbWIpnb1CWq7QVKo88rZ72j28XDWNr2xK1Txn'
    CLERK_AUTHORIZED_PARTIES: Annotated[list[str], NoDecode] = []
    CLERK_WEBHOOK_SIGNING_SECRET: str | None = None
    CLERK_JWT_KEY: str | None = None

    @field_validator("CLERK_AUTHORIZED_PARTIES", mode="before")
    @classmethod
    def _split_csv(cls, v: str | list[str]) -> list[str]:    #this function is used to split the comma saperated domains into list
        if isinstance(v, str):
            return [p.strip() for p in v.split(",") if p.strip()]
        return v





    model_config = SettingsConfigDict(env_file=".env", extra="ignore")  #program automatically finds out the environment variables for the DATAPIPELINE_SERVICE_URL and so onnnn microservices

@lru_cache   #this decorator is used to cache the calucation loaded functions -> simply used to cache functions.
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
