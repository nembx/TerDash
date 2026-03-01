"""System metrics service using psutil."""

import psutil


def get_cpu_percent() -> float:
    """Return current CPU usage percentage."""
    return psutil.cpu_percent(interval=None)


def get_memory_info() -> dict:
    """Return memory usage info."""
    mem = psutil.virtual_memory()
    return {
        "percent": mem.percent,
        "used_gb": mem.used / (1024 ** 3),
        "total_gb": mem.total / (1024 ** 3),
    }
