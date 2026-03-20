# -*- coding: utf-8 -*-

"""Эндпоинт для проверки состояния RabbitMQ."""

from fastapi import APIRouter, HTTPException, status
from app.core import get_module_logger
from app.rabbitmq import (
    get_queues,
    get_connections,
    RabbitMQConnectionError,
    RabbitMQAPIError,
)
from app.utils import calc_level, calc_load_percent

logger = get_module_logger(__name__)

router = APIRouter()


@router.get("/health")
async def health():
    """
    Получить текущее состояние RabbitMQ.

    Returns:
        Объект с количеством сообщений, подключений, процентом нагрузки и цветовым уровнем.

    Raises:
        HTTPException: При ошибке подключения к RabbitMQ.
    """
    try:
        queues = await get_queues()
        connections = await get_connections()
    except (RabbitMQConnectionError, RabbitMQAPIError) as e:
        logger.error(f"Ошибка при получении health: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Не удалось получить данные от RabbitMQ: {str(e)}",
        ) from e

    total_messages = sum(q.get("messages", 0) for q in queues)
    total_consumers = sum(q.get("consumers", 0) for q in queues)

    load_percent = calc_load_percent(total_messages, total_consumers)

    return {
        "messages": total_messages,
        "connections": len(connections),
        "load_percent": load_percent,
        "level": calc_level(load_percent),
    }
