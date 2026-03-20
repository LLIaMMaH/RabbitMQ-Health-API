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
    if Path(settings.log_dir).is_absolute():
        log_dir = Path(settings.log_dir).resolve()
    else:
        # Для Docker: WORKDIR = /app
        # Для локальной разработки: ищем корень проекта
        try:
            # Пытаемся найти корень проекта (где pyproject.toml)
            current = Path(__file__).resolve()
            for parent in [current] + list(current.parents):
                if (parent / "pyproject.toml").exists():
                    log_dir = (parent / settings.log_dir).resolve()
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
        log_file = log_dir / Path(settings.log_file).name
        json_log_file = log_dir / Path(settings.log_json_file).name

        if not ensure_log_dir(log_file.parent):
            settings.log_to_file = False

        if not ensure_log_dir(json_log_file.parent):
            settings.log_to_json = False

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
                "level": settings.log_level_console,
                "format": console_format,
                "colorize": True,
                "filter": _sensitive_filter,
                "enqueue": settings.log_async_logging,
                "backtrace": settings.debug_mode,
                "diagnose": settings.debug_mode,
                "enabled": settings.log_to_console,
            },
            {
                "sink": str(log_file),
                "level": settings.log_level_file,
                "format": (
                    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | "
                    "{module:<30} | {function:<20} | {line:<4} | {message}"
                ),
                "rotation": settings.log_rotation,
                "retention": settings.log_retention,
                "encoding": "utf-8",
                "enqueue": settings.log_async_logging,
                "compression": "zip",
                "filter": _sensitive_filter,
                "backtrace": settings.debug_mode,
                "diagnose": settings.debug_mode,
                "enabled": settings.log_to_file,
            },
            {
                "sink": str(json_log_file),
                "level": settings.log_level_file,
                "serialize": True,
                "rotation": settings.log_rotation,
                "retention": settings.log_retention,
                "encoding": "utf-8",
                "enqueue": settings.log_async_logging,
                "compression": "zip",
                "filter": _sensitive_filter,
                "backtrace": settings.debug_mode,
                "diagnose": settings.debug_mode,
                "enabled": settings.log_to_json,
            },
        ]

        for sink_config in sinks:
            if sink_config["enabled"]:
                logger.add(**{k: v for k, v in sink_config.items() if k != "enabled"})

        if settings.log_capture_exceptions:

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
        default_level = level or ("DEBUG" if settings.debug_mode else "INFO")
        settings.log_level_file = default_level.upper()
        settings.log_level_console = default_level.upper()
        _setup_logger()


def set_log_level(level: str) -> None:
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if level.upper() not in valid_levels:
        raise ValueError(f"Недопустимый уровень логирования: {level}")

    settings.log_level_file = level.upper()
    settings.log_level_console = level.upper()
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
