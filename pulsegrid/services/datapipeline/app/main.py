import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from core.database import connect_to_mongo, disconnect_from_mongo
from core.logging import setup_logging

setup_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):  #lifespan is used to do any setup or initialization tasks that need to be done before the application starts serving requests, and to do any cleanup or shutdown tasks that need to be done after the application stops serving requests

    await connect_to_mongo()
    yield
    await disconnect_from_mongo()


app = FastAPI(title='PulseGrid',description="Your one-stop solution to stay updated in a fast-pacing world—giving you a clear picture of what's happening, every 8 hours",version="1.00",lifespan=lifespan) #initializes the FastAPI application with the lifespan context manager that connects to and disconnects from the MongoDB database asynchronously

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):

    origin = request.headers.get("origin")

    response = JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )

    # Manually re-attach headers so the browser doesn't block the error message
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"

    return response

@app.get('/health-check')
def start():
    logger.info("the server is running strong")

def main():
    print("Hello from bookmyvenue!")

if __name__ == "__main__":
    main()
