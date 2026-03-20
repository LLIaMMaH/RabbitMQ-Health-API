# -*- coding: utf-8 -*-

"""Утилиты для расчёта метрик RabbitMQ."""


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
