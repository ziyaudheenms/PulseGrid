import os
from fastapi import FastAPI
from core.database import connect_to_mongo, disconnect_from_mongo
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):  #lifespan is used to do any setup or initialization tasks that need to be done before the application starts serving requests, and to do any cleanup or shutdown tasks that need to be done after the application stops serving requests

    await connect_to_mongo()
    yield
    await disconnect_from_mongo()


app = FastAPI(title='PulseGrid',description="Your one-stop solution to stay updated in a fast-pacing world—giving you a clear picture of what's happening, every 8 hours",version="1.00",lifespan=lifespan) #initializes the FastAPI application with the lifespan context manager that connects to and disconnects from the MongoDB database asynchronously