FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Установка uv
RUN pip install --no-cache-dir uv

# Копируем только файлы зависимостей
COPY pyproject.toml uv.lock* ./

# Установка зависимостей
RUN uv sync --frozen

# Копируем код
COPY app ./app

EXPOSE 14101

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "14101"]
