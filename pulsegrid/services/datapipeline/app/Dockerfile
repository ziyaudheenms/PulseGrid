# ==========================================
# STAGE 1: Builder (Installs dependencies with uv)
# ==========================================
FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

ARG SERVICE_DIR

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 1. Copy root-level lockfile
COPY uv.lock ./

# 2. Copy service-level pyproject.toml
COPY services/datapipeline/pyproject.toml ./pyproject.toml

# 3. Install dependencies using the root lockfile and service config
RUN uv sync --frozen --no-install-project --no-dev --refresh

# Install bullmq using uv's pip wrapper into the virtual environment
RUN uv pip install --python /app/.venv/bin/python bullmq

# 4. Copy the contents of the service app directory directly into /app builder
COPY ${SERVICE_DIR}/app/ ./


# ==========================================
# STAGE 2: Runtime (Minimal, secure final image)
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

# Create a non-root system user for security hardening
RUN useradd -m appuser

# Copy pre-built virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy flattened application files from builder (main.py, core/, workers/, etc.)
COPY --from=builder /app ./

# Assign ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment paths
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Default command for the API app (runs main:app directly from root /app)
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--loop", "uvloop", \
     "--http", "httptools"]