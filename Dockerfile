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

# Копируем uv из builder
COPY --from=builder /bin/uv /bin/uv

# Копируем установленные зависимости и код
COPY --from=builder /app /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 14101

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "14101"]
