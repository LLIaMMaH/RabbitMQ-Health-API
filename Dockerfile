# syntax=docker/dockerfile:1

# ---------- Builder ----------
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-group dev --no-install-project

COPY . .
RUN uv sync --frozen --no-group dev

# ---------- Runtime ----------
FROM python:3.13-slim

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=builder /opt/venv /opt/venv

RUN groupadd --system appuser && \
    useradd --system --gid appuser --create-home appuser && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app

COPY docker-entrypoint /usr/local/bin/docker-entrypoint
RUN chmod +x /usr/local/bin/docker-entrypoint

WORKDIR /app

COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser static ./static

EXPOSE 14101

ENTRYPOINT ["docker-entrypoint"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "14101"]
