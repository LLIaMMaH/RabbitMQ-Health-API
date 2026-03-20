# -*- coding: utf-8 -*-

"""Модуль настроек приложения RabbitMQ Health API."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
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
    api_base_path: str = "/api/rabbitmq"
    api_port: int = 14101

    # ======================================================
    # RabbitMQ
    # ======================================================
    rabbitmq_host: str = "127.0.0.1"
    rabbitmq_port: int = 15672
    rabbitmq_user: str
    rabbitmq_password: SecretStr

    # ======================================================
    # Runtime
    # ======================================================
    env: str = "dev"

    # ======================================================
    # Debug
    # ======================================================
    debug_mode: bool = False

    # ======================================================
    # Logging
    # ======================================================
    log_dir: str = "logs"
    log_file: str = "app.log"
    log_json_file: str = "app.json"

    log_to_file: bool = True
    log_to_console: bool = True
    log_to_json: bool = False

    log_rotation: str = "50 MB"
    log_retention: str = "30 days"

    log_level_file: str = "INFO"
    log_level_console: str = "INFO"

    log_async_logging: bool = True
    log_capture_exceptions: bool = True

    log_custom_sinks: List[str] = []


@lru_cache
def get_settings() -> Settings:
    """Получить кэшированные настройки приложения."""
    return Settings()


settings = get_settings()
