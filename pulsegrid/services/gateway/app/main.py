from fastapi import FastAPI
from core.config import settings
from api.v1.datapipeline.router import router as datapipeline_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Register downstream routers
app.include_router(datapipeline_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}


def main():
    print("Hello from gateway!")


if __name__ == "__main__":
    main()
