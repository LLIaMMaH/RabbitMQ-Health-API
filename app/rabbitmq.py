# -*- coding: utf-8 -*-

import httpx
from app.config import settings

BASE_URL = f"http://{settings.rabbitmq_host}:{settings.rabbitmq_port}/api"

auth = (settings.rabbitmq_user, settings.rabbitmq_password)


async def get_overview():
    async with httpx.AsyncClient(auth=auth, timeout=5) as client:
        r = await client.get(f"{BASE_URL}/overview")
        r.raise_for_status()
        return r.json()


async def get_queues():
    async with httpx.AsyncClient(auth=auth, timeout=5) as client:
        r = await client.get(f"{BASE_URL}/queues")
        r.raise_for_status()
        return r.json()


async def get_connections():
    async with httpx.AsyncClient(auth=auth, timeout=5) as client:
        r = await client.get(f"{BASE_URL}/connections")
        r.raise_for_status()
        return r.json()
