# -*- coding: utf-8 -*-

"""Модуль настроек приложения RabbitMQ Health API."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Настройки приложения RabbitMQ Health API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ======================================================
    # API
    # ======================================================
    api_base_path: str = Field(
        default="/api/rabbitmq",
        description="Базовый путь API",
    )
    api_port: int = Field(
        default=14101,
        description="Порт для запуска API",
        ge=1,
        le=65535,
    )

    # ======================================================
    # RabbitMQ
    # ======================================================
    rabbitmq_host: str = Field(
        default="127.0.0.1",
        description="Хост RabbitMQ",
    )
    rabbitmq_port: int = Field(
        default=15672,
        description="Порт RabbitMQ Management API",
        ge=1,
        le=65535,
    )
    rabbitmq_user: str = Field(
        ...,
        description="Пользователь RabbitMQ (из .env)",
    )
    rabbitmq_password: SecretStr = Field(
        ...,
        description="Пароль RabbitMQ (из .env)",
    )

    # ======================================================
    # Runtime
    # ======================================================
    env: str = Field(
        default="dev",
        description="Окружение (dev/prod)",
    )

    # ======================================================
    # Debug
    # ======================================================
    debug_mode: bool = Field(
        default=False,
        description="Режим отладки",
    )

    # ======================================================
    # Logging
    # ======================================================
    log_dir: str = Field(
        default="logs",
        description="Директория для логов",
    )
    log_file: str = Field(
        default="app.log",
        description="Имя файла лога",
    )
    log_json_file: str = Field(
        default="app.json",
        description="Имя файла JSON лога",
    )

    log_to_file: bool = Field(
        default=True,
        description="Логирование в файл",
    )
    log_to_console: bool = Field(
        default=True,
        description="Логирование в консоль",
    )
    log_to_json: bool = Field(
        default=False,
        description="Логирование в JSON формате",
    )

    log_rotation: str = Field(
        default="50 MB",
        description="Ротация логов (размер)",
    )
    log_retention: str = Field(
        default="30 days",
        description="Хранение логов (время)",
    )

    log_level_file: str = Field(
        default="INFO",
        description="Уровень логирования для файла",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )
    log_level_console: str = Field(
        default="INFO",
        description="Уровень логирования для консоли",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )

    log_async_logging: bool = Field(
        default=True,
        description="Асинхронное логирование",
    )
    log_capture_exceptions: bool = Field(
        default=True,
        description="Перехват необработанных исключений",
    )

    log_custom_sinks: List[str] = Field(
        default_factory=list,
        description="Пользовательские приёмники логов",
    )


@lru_cache
def get_settings() -> Settings:
    """Получить кэшированные настройки приложения."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
