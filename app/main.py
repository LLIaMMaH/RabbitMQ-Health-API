# -*- coding: utf-8 -*-

from fastapi import FastAPI
from app.config import settings
from app.routes import health, status, metrics

app = FastAPI()

app.include_router(health.router, prefix=settings.api_base_path)
app.include_router(status.router, prefix=settings.api_base_path)
app.include_router(metrics.router, prefix=settings.api_base_path)
