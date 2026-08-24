"""
Data pipeline worker is used to listen for the datapipeline queue and process the tasks provided in it respectiveky
as needed..



CHALLENGE :- since the backgorund queue and the worker system is running in a saperate system we cant use any thing like 
the DB redis that is initialissed in the fastapi instance

    - have to run the connect_to_mongo() to establish the cient
    - have to get the db session and redis session
    - have to clean them up on the stoping of the worker

"""
import asyncio

import structlog
from bullmq import Worker

from core.database import connect_to_mongo, disconnect_from_mongo
from tasks.data_fetch import route_data_fetch_task
from core.config import settings
from core.logging import setup_logging

setup_logging()
logger = structlog.get_logger()

def handle_completed(job, result):
    logger.info("Successfully completed the backend processing!", job_id = job['jobId'])

def handle_failed(job, err):
    logger.info("Opps! Failed the processing, Some kind of error happened", job_id = job['jobId'])


async def start_worker():
    print("Starting the DATAPIPELINE worker")
    print("Creating the DB client")
    await connect_to_mongo()

    worker = Worker(
        'data_pipeline',
        route_data_fetch_task, # type: ignore[arg-type]
        {
            "connection": settings.DATAPIPELINE_TASK_REDIS_TCP_URL,
            "concurrency": 1
        }
    )
    print(f"Worker initialized with redis connections : {settings.DATAPIPELINE_TASK_REDIS_TCP_URL}")
    print(f"Sytem is ready to process the jobs..........")

    # Tracing the status of the worker instance
    worker.on("completed", handle_completed)
    worker.on("failed", handle_failed)
    
    try:
        await asyncio.Event().wait()    #this config is used to pause the work and wait for new events or new tasks , it is used to prevent the code from stopping the  execution after a initial setup run
    except (KeyboardInterrupt, asyncio.CancelledError):
        await disconnect_from_mongo()  #disconnecting from the mongo db client.
        await worker.close()   #forcfully stoping the worker when a keyboard key (Ctrl + C) is pressed or any cancell error happens

if __name__ == "__main__":
    asyncio.run(start_worker())  #running the start_worker as a asyncio function....
    

