# -*- coding: utf-8 -*-

"""Утилиты для расчёта метрик RabbitMQ."""

CONST_BYTES_IN_KB = 1024
CONST_BYTES_IN_MB = 1024**2
CONST_BYTES_IN_GB = 1024**3


def calc_level(percent: float) -> str:
    """
    Рассчитать цветовой уровень нагрузки.

    Args:
        percent: Процент нагрузки (0-100).

    Returns:
        Цветовой индикатор:
        - 🟢 green: до 50%
        - 🟡 yellow: 51-75%
        - 🔴 red: 76% и выше
    """
    if percent <= 50:
        return "🟢"
    if percent <= 75:
        return "🟡"
    return "🔴"


def calc_load_percent(total_messages: int, total_consumers: int) -> float:
    """
    Рассчитать процент нагрузки на брокер.

    Args:
        total_messages: Общее количество сообщений в очередях.
        total_consumers: Общее количество потребителей.

    Returns:
        Процент нагрузки (0-100).

    Примечание:
        Условная ёмкость рассчитывается как: consumers * 100 сообщений.
    """
    capacity = max(total_consumers * 100, 1)
    load_percent = min((total_messages / capacity) * 100, 100)
    return round(load_percent, 2)


def bytes_to_mb(bytes_value: int) -> int:
    """
    Конвертировать байты в мегабайты.

    Args:
        bytes_value: Значение в байтах.

    Returns:
        Значение в мегабайтах.
    """
    return bytes_value // CONST_BYTES_IN_MB


def bytes_to_gb(bytes_value: int) -> int:
    """
    Конвертировать байты в гигабайты.

    Args:
        bytes_value: Значение в байтах.

    Returns:
        Значение в гигабайтах.
    """
    return bytes_value // CONST_BYTES_IN_GB
