# -*- coding: utf-8 -*-

import psutil


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
            "total_mb": mem.total // 1024 // 1024,
            "used_mb": mem.used // 1024 // 1024,
            "usage_percent": mem.percent,
        },
        "disk": {
            "total_gb": disk.total // 1024 // 1024 // 1024,
            "used_gb": disk.used // 1024 // 1024 // 1024,
            "usage_percent": disk.percent,
        },
    }
