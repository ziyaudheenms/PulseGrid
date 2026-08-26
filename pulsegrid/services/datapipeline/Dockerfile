# syntax=docker/dockerfile:1.9

# 1. Builder Stage
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Mount root uv.lock AND the service's pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=services/datapipeline/pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy application source code and service configuration
COPY services/datapipeline/app ./app
COPY services/datapipeline/pyproject.toml ./pyproject.toml
COPY uv.lock ./uv.lock

# Install service package from lockfile first, then overlay bullmq using uv pip
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable && \
    uv pip install --python /app/.venv bullmq

# 2. Runtime Stage
FROM python:3.12-slim AS runtime

RUN groupadd -g 1001 app && \
    useradd -u 1001 -g app -m -d /app -s /bin/false app

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/app" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/app /app/app

USER app

EXPOSE 8000

# HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
#     CMD python -c "import httpx; httpx.get('http://127.0.0.1:8000/health-check', timeout=60)" || exit 1

CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--loop", "uvloop", \
     "--http", "httptools"]