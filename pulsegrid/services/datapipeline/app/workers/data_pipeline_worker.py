"""
Data pipeline worker is used to listen for the datapipeline queue and process the tasks provided in it respectiveky
as needed..



CHALLENGE :- since the backgorund queue and the worker system is running in a saperate system we cant use any thing like 
the DB redis that is initialissed in the fastapi instance

    - have to run the connect_to_mongo() to establish the cient
    - have to get the db session and redis session
    - have to clean them up on the stoping of the worker

"""


from core.database import connect_to_mongo, disconnect_from_mongo
from tasks.data_fetch import route_data_fetch_task
from core.config import settings
# from core.logging import setup_logging

# setup_logging()
# logger = structlog.get_logger()

# def handle_completed(job, result):
#     logger.info("Successfully completed the backend processing!", job_id = job['jobId'])

# def handle_failed(job, err):
#     logger.info("Opps! Failed the processing, Some kind of error happened", job_id = job['jobId'])


# async def start_worker():
#     print("Starting the DATAPIPELINE worker")
#     print("Creating the DB client")
#     await connect_to_mongo()

#     worker = Worker(
#         'data_pipeline',
#         route_data_fetch_task, # type: ignore[arg-type]
#         {
#             "connection": settings.DATAPIPELINE_TASK_REDIS_TCP_URL,
#             "concurrency": 1
#         }
#     )
#     print(f"Worker initialized with redis connections : {settings.DATAPIPELINE_TASK_REDIS_TCP_URL}")
#     print(f"Sytem is ready to process the jobs..........")

#     # Tracing the status of the worker instance
#     worker.on("completed", handle_completed)
#     worker.on("failed", handle_failed)
    
#     try:
#         await asyncio.Event().wait()    #this config is used to pause the work and wait for new events or new tasks , it is used to prevent the code from stopping the  execution after a initial setup run
#     except (KeyboardInterrupt, asyncio.CancelledError):
#         await disconnect_from_mongo()  #disconnecting from the mongo db client.
#         await worker.close()   #forcfully stoping the worker when a keyboard key (Ctrl + C) is pressed or any cancell error happens

# if __name__ == "__main__":
#     asyncio.run(start_worker())  #running the start_worker as a asyncio function....
    

import asyncio
import os
from datetime import datetime
from bullmq import Worker, Job
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich import box

console = Console()

# Product Metadata
PRODUCT_NAME = "PULSEGRID ENGINE"
PRODUCT_DESC = "Automated Data Extraction & Distributed Web Crawler Pipeline"
WORKER_NAME = "data_pipeline"
CONCURRENCY = 5
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").upper()
REDIS_HOST = "upstash-redis.io"

def build_header_panel() -> Panel:
    """Builds a sharp, structured product status dashboard."""
    
    # 1. Clean ASCII Brand Header
    brand_text = Text()
    brand_text.append("█▀█ █  █ █   █▀▀ █▀▀ █▀▀ █▀█ █ █▀▄\n", style="bold cyan")
    brand_text.append("█▀▀ █▄▄█ █▄▄ ██▄ █▄█ █▀█ █▀▄ █ █▄▀", style="bold cyan")

    # 2. Key-Value Info Grid
    info_table = Table(box=None, show_header=False, pad_edge=False, padding=(0, 2))
    info_table.add_column("Property", style="bold dim white")
    info_table.add_column("Value")

    info_table.add_row("Service", f"[bold white]{PRODUCT_NAME}[/bold white]")
    info_table.add_row("Description", f"[dim]{PRODUCT_DESC}[/dim]")
    info_table.add_row("Target Queue", f"[bold magenta]{WORKER_NAME}[/bold magenta]")
    info_table.add_row("Concurrency", f"[bold yellow]{CONCURRENCY} Parallel Threads[/bold yellow]")
    info_table.add_row("Environment", f"[bold blue]{ENVIRONMENT}[/bold blue]")
    info_table.add_row("Broker Host", f"[dim white]{REDIS_HOST}[/dim white]")

    # 3. Combine Into Side-by-Side Table Layout
    main_grid = Table.grid(expand=True)
    main_grid.add_column(ratio=1)
    main_grid.add_column(ratio=2)
    
    main_grid.add_row(
        Panel(brand_text, box=box.SIMPLE, border_style="cyan"),
        info_table
    )

    return Panel(
        main_grid,
        title="[bold white on cyan] SYSTEM WORKER NODE [/bold white on cyan]",
        title_align="left",
        subtitle="[bold green]● STATUS: ONLINE[/bold green]",
        subtitle_align="right",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    )

def log_event(status: str, job: Job, detail: str = ""):
    """Standardized production log stream printer."""
    now = datetime.now().strftime("%H:%M:%S")
    
    if status == "SUCCESS":
        badge = "[bold white on green]  OK  [/bold white on green]"
    else:
        badge = "[bold white on red] FAIL [/bold white on red]"

    console.print(
        f"[dim]{now}[/dim] {badge} "
        f"[bold cyan]ID:{job.id}[/bold cyan] "
        f"[bold white]{job.name:<20}[/bold white] "
        f"[dim]➔ {detail}[/dim]"
    )

def handle_completed(job: Job, result: str):
    log_event("SUCCESS", job, str(result))

def handle_failed(job: Job, err: Exception):
    log_event("FAILED", job, str(err))

async def start_worker():
    
    console.clear()
    console.print(build_header_panel())
    await connect_to_mongo()
    
    console.print("\n[bold dim white]─── LIVE STREAM LOGS ───────────────────────────────────────────[/bold dim white]\n")

    worker = Worker(
        WORKER_NAME,
        route_data_fetch_task, # type: ignore[arg-type]
        {"connection": settings.DATAPIPELINE_TASK_REDIS_TCP_URL, "concurrency": CONCURRENCY}
    )

    worker.on("completed", handle_completed)
    worker.on("failed", handle_failed)

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        console.print("\n")
        console.print(
            Panel(
                "[bold yellow]⚠️ Shutdown signal received. Gracefully terminating worker...[/bold yellow]",
                border_style="yellow",
                box=box.ROUNDED,
                expand=False
            )
        )
        await worker.close()
        await disconnect_from_mongo()
        console.print("[bold red]🛑 Service offline.[/bold red]")

if __name__ == "__main__":
    asyncio.run(start_worker())