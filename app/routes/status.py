# -*- coding: utf-8 -*-

from fastapi import APIRouter
from app.rabbitmq import get_overview, get_queues, get_connections

router = APIRouter()


@router.get("/status")
async def status():
    overview = await get_overview()
    queues = await get_queues()
    connections = await get_connections()

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
