# -*- coding: utf-8 -*-

"""RabbitMQ Health API — сервис для мониторинга RabbitMQ и ВМ."""

from fastapi import FastAPI
from app.core import settings, init_logger, get_module_logger
from app.routes import health, status, metrics

# Инициализация логгера
init_logger()

logger = get_module_logger(__name__)

app = FastAPI(
    title="RabbitMQ Health API",
    description="Сервис для мониторинга RabbitMQ и состояния виртуальной машины",
    version="0.1.0",
)

app.include_router(health.router, prefix=settings.api_base_path)
app.include_router(status.router, prefix=settings.api_base_path)
app.include_router(metrics.router, prefix=settings.api_base_path)


@app.on_event("startup")
async def startup_event():
    """Событие при запуске приложения."""
    logger.info(f"Запуск RabbitMQ Health API на порту {settings.api_port}")
    logger.info(f"Base path: {settings.api_base_path}")
    logger.info(f"RabbitMQ host: {settings.rabbitmq_host}:{settings.rabbitmq_port}")


@app.on_event("shutdown")
async def shutdown_event():
    """Событие при остановке приложения."""
    logger.info("Остановка RabbitMQ Health API")
