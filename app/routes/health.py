# -*- coding: utf-8 -*-

from fastapi import APIRouter
from app.rabbitmq import get_queues, get_connections
from app.utils import calc_level, calc_load_percent

router = APIRouter()


@router.get("/health")
async def health():
    queues = await get_queues()
    connections = await get_connections()

    total_messages = sum(q.get("messages", 0) for q in queues)
    total_consumers = sum(q.get("consumers", 0) for q in queues)

    load_percent = calc_load_percent(total_messages, total_consumers)

    return {
        "messages": total_messages,
        "connections": len(connections),
        "load_percent": load_percent,
        "level": calc_level(load_percent),
    }
