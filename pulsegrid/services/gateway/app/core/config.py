from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "PulseGrid API Gateway"
    VERSION: str = "1.0.0"

    # Microservice Target URLs
    DATAPIPELINE_SERVICE_URL: str = "http://localhost:8000"
    DATAPIPELINE_VERSION: str = "v1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")  #program automatically finds out the environment variables for the DATAPIPELINE_SERVICE_URL and so onnnn microservices

settings = Settings()
