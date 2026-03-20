# -*- coding: utf-8 -*-

import psutil
from app.utils import bytes_to_mb, bytes_to_gb


def collect_metrics():
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return {
        "cpu": {
            "usage_percent": cpu,
            "cores": psutil.cpu_count(),
        },
        "memory": {
            "total_mb": bytes_to_mb(mem.total),
            "used_mb": bytes_to_mb(mem.used),
            "usage_percent": mem.percent,
        },
        "disk": {
            "total_gb": bytes_to_gb(disk.total),
            "used_gb": bytes_to_gb(disk.used),
            "usage_percent": disk.percent,
        },
    }
