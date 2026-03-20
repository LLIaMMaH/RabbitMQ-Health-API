# -*- coding: utf-8 -*-

"""Клиент для взаимодействия с RabbitMQ Management API."""

import httpx
from app.core import settings, get_module_logger

logger = get_module_logger(__name__)

BASE_URL = f"http://{settings.rabbitmq_host}:{settings.rabbitmq_port}/api"

auth = (settings.rabbitmq_user, settings.rabbitmq_password.get_secret_value())


class RabbitMQConnectionError(Exception):
    """Исключение при ошибке подключения к RabbitMQ."""

    pass


class RabbitMQAPIError(Exception):
    """Исключение при ошибке запроса к RabbitMQ API."""

    pass


async def get_overview() -> dict:
    """
    Получить общую информацию о RabbitMQ.

    Returns:
        JSON с информацией о брокере.

    Raises:
        RabbitMQConnectionError: При ошибке подключения.
        RabbitMQAPIError: При ошибке запроса к API.
    """
    try:
        async with httpx.AsyncClient(auth=auth, timeout=5) as client:
            r = await client.get(f"{BASE_URL}/overview")
            r.raise_for_status()
            return r.json()
    except httpx.ConnectError as e:
        logger.error(f"Не удалось подключиться к RabbitMQ: {e}")
        raise RabbitMQConnectionError(f"Ошибка подключения к RabbitMQ: {e}") from e
    except httpx.HTTPStatusError as e:
        logger.error(f"Ошибка HTTP при запросе overview: {e}")
        raise RabbitMQAPIError(f"Ошибка API RabbitMQ: {e}") from e
    except httpx.RequestError as e:
        logger.error(f"Ошибка запроса к RabbitMQ: {e}")
        raise RabbitMQAPIError(f"Ошибка запроса: {e}") from e


async def get_queues() -> list:
    """
    Получить список очередей.

    Returns:
        Список очередей.

    Raises:
        RabbitMQConnectionError: При ошибке подключения.
        RabbitMQAPIError: При ошибке запроса к API.
    """
    try:
        async with httpx.AsyncClient(auth=auth, timeout=5) as client:
            r = await client.get(f"{BASE_URL}/queues")
            r.raise_for_status()
            return r.json()
    except httpx.ConnectError as e:
        logger.error(f"Не удалось подключиться к RabbitMQ: {e}")
        raise RabbitMQConnectionError(f"Ошибка подключения к RabbitMQ: {e}") from e
    except httpx.HTTPStatusError as e:
        logger.error(f"Ошибка HTTP при запросе queues: {e}")
        raise RabbitMQAPIError(f"Ошибка API RabbitMQ: {e}") from e
    except httpx.RequestError as e:
        logger.error(f"Ошибка запроса к RabbitMQ: {e}")
        raise RabbitMQAPIError(f"Ошибка запроса: {e}") from e


async def get_connections() -> list:
    """
    Получить список подключений.

    Returns:
        Список подключений.

    Raises:
        RabbitMQConnectionError: При ошибке подключения.
        RabbitMQAPIError: При ошибке запроса к API.
    """
    try:
        async with httpx.AsyncClient(auth=auth, timeout=5) as client:
            r = await client.get(f"{BASE_URL}/connections")
            r.raise_for_status()
            return r.json()
    except httpx.ConnectError as e:
        logger.error(f"Не удалось подключиться к RabbitMQ: {e}")
        raise RabbitMQConnectionError(f"Ошибка подключения к RabbitMQ: {e}") from e
    except httpx.HTTPStatusError as e:
        logger.error(f"Ошибка HTTP при запросе connections: {e}")
        raise RabbitMQAPIError(f"Ошибка API RabbitMQ: {e}") from e
    except httpx.RequestError as e:
        logger.error(f"Ошибка запроса к RabbitMQ: {e}")
        raise RabbitMQAPIError(f"Ошибка запроса: {e}") from e
