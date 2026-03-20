# -*- coding: utf-8 -*-
"""
Модуль логирования для проекта.
Поддерживает три приёмника: консоль, файл и JSON.

Пример использования:
```python
from app.core.logging import get_module_logger, set_log_level

logger = get_module_logger(__name__)
logger.info("Сообщение для логирования")
set_log_level("DEBUG")  # Установить уровень логирования
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import settings
from loguru import logger

_logger_initialized = False


class LoggingSetupError(Exception):
    """Исключение для ошибок настройки логирования."""

    pass


def ensure_log_dir(path: str | Path) -> bool:
    path = Path(path)
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".test_write"
        with test_file.open("w") as f:
            f.write("test")
        test_file.unlink()
        return True
    except (OSError, PermissionError) as e:
        print(f"[ERROR] Не удалось создать или записать в {path}: {e}", file=sys.stderr)
        return False


def _get_default_log_dir() -> Path:
    """
    Получить абсолютный путь к директории логов.

    Returns:
        Абсолютный путь к папке с логами.
    """
    # Если LOG_DIR абсолютный путь — используем его
    if Path(settings.LOG_DIR).is_absolute():
        log_dir = Path(settings.LOG_DIR).resolve()
    else:
        # Для Docker: WORKDIR = /app
        # Для локальной разработки: ищем корень проекта
        try:
            # Пытаемся найти корень проекта (где pyproject.toml)
            current = Path(__file__).resolve()
            for parent in [current] + list(current.parents):
                if (parent / "pyproject.toml").exists():
                    log_dir = (parent / settings.LOG_DIR).resolve()
                    break
            else:
                # Fallback: используем /app/logs для Docker
                log_dir = Path("/app/logs").resolve()
        except Exception:
            # Fallback: используем /app/logs для Docker
            log_dir = Path("/app/logs").resolve()

    if ensure_log_dir(log_dir):
        return log_dir
    raise LoggingSetupError(f"Директория логов недоступна: {log_dir}")


def _sensitive_filter(record: Dict[str, Any]) -> bool:
    message = record.get("message", "")

    sensitive_patterns = [
        (re.compile(r"(password\s*=\s*)(\S+)", re.IGNORECASE), r"\1****"),
        (re.compile(r"(token\s*=\s*)(\S+)", re.IGNORECASE), r"\1****"),
        (re.compile(r"\b\d{16}\b"), "****"),
        (re.compile(r"(postgresql\+?\w*://[^:]+:)([^@]+)(@)"), r"\1****\3"),
    ]

    for pattern, repl in sensitive_patterns:
        message = pattern.sub(repl, message)

    record["message"] = message
    return True


def _setup_logger() -> None:
    global _logger_initialized

    if _logger_initialized:
        return

    try:
        log_dir = _get_default_log_dir()
        log_file = log_dir / Path(settings.LOG_FILE).name
        json_log_file = log_dir / Path(settings.LOG_JSON_FILE).name

        if not ensure_log_dir(log_file.parent):
            settings.LOG_TO_FILE = False

        if not ensure_log_dir(json_log_file.parent):
            settings.LOG_TO_JSON = False

        logger.remove()

        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level:<8}</level> | "
            "<cyan>{module:<30}</cyan> | "
            "<cyan>{function:<20}</cyan> | "
            "<cyan>{line:<4}</cyan> | "
            "<level>{message}</level>"
        )

        sinks = [
            {
                "sink": sys.stderr,
                "level": settings.LOG_LEVEL_CONSOLE,
                "format": console_format,
                "colorize": True,
                "filter": _sensitive_filter,
                "enqueue": settings.LOG_ASYNC_LOGGING,
                "backtrace": settings.DEBUG_MODE,
                "diagnose": settings.DEBUG_MODE,
                "enabled": settings.LOG_TO_CONSOLE,
            },
            {
                "sink": str(log_file),
                "level": settings.LOG_LEVEL_FILE,
                "format": (
                    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | "
                    "{module:<30} | {function:<20} | {line:<4} | {message}"
                ),
                "rotation": settings.LOG_ROTATION,
                "retention": settings.LOG_RETENTION,
                "encoding": "utf-8",
                "enqueue": settings.LOG_ASYNC_LOGGING,
                "compression": "zip",
                "filter": _sensitive_filter,
                "backtrace": settings.DEBUG_MODE,
                "diagnose": settings.DEBUG_MODE,
                "enabled": settings.LOG_TO_FILE,
            },
            {
                "sink": str(json_log_file),
                "level": settings.LOG_LEVEL_FILE,
                "serialize": True,
                "rotation": settings.LOG_ROTATION,
                "retention": settings.LOG_RETENTION,
                "encoding": "utf-8",
                "enqueue": settings.LOG_ASYNC_LOGGING,
                "compression": "zip",
                "filter": _sensitive_filter,
                "backtrace": settings.DEBUG_MODE,
                "diagnose": settings.DEBUG_MODE,
                "enabled": settings.LOG_TO_JSON,
            },
        ]

        for sink_config in sinks:
            if sink_config["enabled"]:
                logger.add(**{k: v for k, v in sink_config.items() if k != "enabled"})

        if settings.LOG_CAPTURE_EXCEPTIONS:

            def log_excepthook(exc_type, exc_value, exc_traceback):
                logger.bind(module="excepthook").opt(
                    exception=(exc_type, exc_value, exc_traceback)
                ).error("Необработанное исключение")

            sys.excepthook = log_excepthook

        _logger_initialized = True

    except Exception as e:
        print(f"[ERROR] Не удалось настроить логгер: {e}", file=sys.stderr)
        raise LoggingSetupError(f"Ошибка настройки логгера: {e}")


def init_logger(level: Optional[str] = None) -> None:
    global _logger_initialized

    if not _logger_initialized:
        default_level = level or ("DEBUG" if settings.DEBUG_MODE else "INFO")
        settings.LOG_LEVEL_FILE = default_level.upper()
        settings.LOG_LEVEL_CONSOLE = default_level.upper()
        _setup_logger()


def set_log_level(level: str) -> None:
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if level.upper() not in valid_levels:
        raise ValueError(f"Недопустимый уровень логирования: {level}")

    settings.LOG_LEVEL_FILE = level.upper()
    settings.LOG_LEVEL_CONSOLE = level.upper()
    logger.remove()
    _setup_logger()


def get_module_logger(module_name: Optional[str] = None):
    import inspect

    global _logger_initialized

    if not _logger_initialized:
        init_logger()

    if module_name is None:
        frame = inspect.currentframe()
        if frame and frame.f_back:
            module_name = frame.f_back.f_globals.get("__name__", "unknown")
        else:
            module_name = "unknown"

    return logger.bind(module=module_name)


__all__ = [
    "get_module_logger",
    "LoggingSetupError",
    "init_logger",
    "set_log_level",
]
