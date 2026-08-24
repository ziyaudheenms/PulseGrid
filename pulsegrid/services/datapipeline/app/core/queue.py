"""
This file is used for the configuration of bullmq Queues that is to be used for the
background processing , and so on......

Was using celery but since this project completely relies on async functions we are decided to switch towared bullmq

Here we have to define all the queues and will be initiallied when the lifescyle of the fastapi gets started.
"""

from typing import Dict

from bullmq import Queue

from .config import settings

#resigtry that is used to keep the record of active queues that are present
queues: Dict[str, Queue] = {}


def init_queues() -> Dict[str, Queue]:
    """
        this fucntion is used to initalize all the Queues which we have
    """

    #initializing the queues we need
    queues['data_pipeline'] = Queue(name = "data_pipeline", opts = {"connection":settings.DATAPIPELINE_TASK_REDIS_TCP_URL })

    return queues

async def close_queues() -> None:
    """
        Using this function we close all the connectios to the queue one by one
    """
    for name, queue in queues.items():
        await queue.close()  # closing the queue connection

    queues.clear() # used to clear the entire registry.


def get_queue(name: str) -> Queue:
    """
    this handle is used to pick the queue that is being asked from the queue registry
    """

    if not name in queues.keys():
        raise RuntimeError(f"Queue named with {name} is not found in the registry.......")

    return queues[name]
