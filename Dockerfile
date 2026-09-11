# Stage 1: Build virtual environment using uv
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Patch OS packages to remediate upstream CVEs
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Install dependencies first for optimal Docker layer caching
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy application source and data
COPY src/ ./src/
COPY data/ ./data/

# Sync the full project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Stage 2: Minimal runtime image
FROM python:3.12-slim-bookworm AS runtime

# Security: patch OS packages and create unprivileged user
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

WORKDIR /app

# Copy virtual environment and app files from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/src /app/src
COPY --from=builder --chown=appuser:appuser /app/data /app/data

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    GRADIO_SERVER_NAME="0.0.0.0" \
    GRADIO_SERVER_PORT="7860"

USER appuser

EXPOSE 7860

CMD ["python", "src/app.py"]