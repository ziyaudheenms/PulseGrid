# ==========================================
# STAGE 1: Builder (Installs dependencies with uv)
# ==========================================
FROM ghcr.io/astral-sh/uv:python3.11-slim AS builder

WORKDIR /app

ARG SERVICE_DIR

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 1. Copy root-level lockfile
COPY uv.lock ./

# 2. Copy service-level pyproject.toml
COPY ${SERVICE_DIR}/pyproject.toml ./pyproject.toml

# 3. Install dependencies using the root lockfile and service config
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# 4. Copy the entire gateway app source code folder
COPY ${SERVICE_DIR}/app ./app


# ==========================================
# STAGE 2: Runtime (Minimal, secure final image)
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

# Create a non-root system user for security hardening
RUN useradd -m appuser

# Copy pre-built virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code from builder
COPY --from=builder /app/app ./app

# Assign ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment paths
ENV PATH="/app/.venv/bin:$PATH"

# PUBLIC EDGE: Expose port 8000 internally to allow incoming client traffic
EXPOSE 8000

# High-performance Uvicorn startup command with uvloop and httptools
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--loop", "uvloop", "--http", "httptools"]