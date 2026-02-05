# -*- coding: utf-8 -*-

from fastapi import APIRouter
from app.metrics import collect_metrics

router = APIRouter()


@router.get("/metrics")
def metrics():
    return collect_metrics()
