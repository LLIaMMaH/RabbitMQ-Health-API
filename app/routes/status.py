# -*- coding: utf-8 -*-

"""Эндпоинт для получения подробной информации о RabbitMQ."""

from fastapi import APIRouter, HTTPException, status as http_status
from app.core import get_module_logger
from app.rabbitmq import (
    get_overview,
    get_queues,
    get_connections,
    RabbitMQConnectionError,
    RabbitMQAPIError,
)

logger = get_module_logger(__name__)

router = APIRouter()


@router.get("/status")
async def get_status():
    """
    Получить подробную информацию о RabbitMQ.

    Returns:
        Объект с информацией о версии, uptime, очередях и подключениях.

    Raises:
        HTTPException: При ошибке подключения к RabbitMQ.
    """
    try:
        overview = await get_overview()
        queues = await get_queues()
        connections = await get_connections()
    except (RabbitMQConnectionError, RabbitMQAPIError) as e:
        logger.error(f"Ошибка при получении status: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Не удалось получить данные от RabbitMQ: {str(e)}",
        ) from e

    return {
        "rabbitmq": {
            "version": overview.get("rabbitmq_version"),
            "node": overview.get("node"),
            "uptime_seconds": overview.get("uptime"),
        },
        "queues": [
            {
                "name": q["name"],
                "vhost": q["vhost"],
                "messages": q["messages"],
                "messages_ready": q["messages_ready"],
                "messages_unacknowledged": q["messages_unacknowledged"],
                "consumers": q["consumers"],
            }
            for q in queues
        ],
        "connections": {
            "total": len(connections),
        },
    }
