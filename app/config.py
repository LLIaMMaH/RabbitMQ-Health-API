# -*- coding: utf-8 -*-

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from functools import lru_cache


class Settings(BaseSettings):
    """Настройки приложения RabbitMQ Health API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API
    api_base_path: str = "/api/rabbitmq"
    api_port: int = 14101

    # RabbitMQ
    rabbitmq_host: str = "127.0.0.1"
    rabbitmq_port: int = 15672
    rabbitmq_user: str
    rabbitmq_password: SecretStr

    # Runtime
    env: str = "dev"


@lru_cache
def get_settings() -> Settings:
    """Получить кэшированные настройки приложения."""
    return Settings()


settings = get_settings()
