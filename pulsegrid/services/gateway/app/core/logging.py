import logging
import sys
import structlog


def setup_logging() -> None:

    is_production = True

    processors = [
        structlog.contextvars.merge_contextvars, # Pulls metadata like request_id automatically
        structlog.processors.add_log_level,       # Adds "level": "INFO"
        structlog.processors.TimeStamper(fmt="iso"), # Adds ISO 8601 UTC timestamp
        structlog.processors.StackInfoRenderer(),   # Captures call stack on errors
        structlog.processors.format_exc_info,       # Gracefully serializes traceback objects
    ]

    if is_production:
        # Production Pipeline: Stream pure JSON strings
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development Pipeline: Stream colored, readable lines
        processors.append(structlog.dev.ConsoleRenderer(colors=True))


    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,  #output the log in the terminal
        level=logging.INFO,
    )
