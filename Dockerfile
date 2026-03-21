# Stage 1: Build
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

# Копируем только файлы зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей
RUN uv sync --frozen

# Копируем код
COPY app ./app


# Stage 2: Runtime
FROM python:3.13-slim

WORKDIR /app

# Копируем виртуальное окружение и код из builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 14101

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "14101"]
