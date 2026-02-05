# -*- coding: utf-8 -*-

from fastapi import APIRouter
from app.rabbitmq import get_queues, get_connections

router = APIRouter()


def calc_level(percent: float) -> str:
    if percent <= 50:
        return "🟢"
    if percent <= 75:
        return "🟡"
    return "🔴"


@router.get("/health")
async def health():
    queues = await get_queues()
    connections = await get_connections()

    total_messages = sum(q.get("messages", 0) for q in queues)
    total_consumers = sum(q.get("consumers", 0) for q in queues)

    # Условная ёмкость: consumers * 100 сообщений
    capacity = max(total_consumers * 100, 1)
    load_percent = min((total_messages / capacity) * 100, 100)

    return {
        "messages": total_messages,
        "connections": len(connections),
        "load_percent": round(load_percent, 2),
        "level": calc_level(load_percent),
    }
