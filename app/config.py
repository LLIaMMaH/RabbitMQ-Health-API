# -*- coding: utf-8 -*-

from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    api_base_path: str = os.getenv("API_BASE_PATH", "/api/rabbitmq")
    api_port: int = int(os.getenv("API_PORT", 14101))

    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "127.0.0.1")
    rabbitmq_port: int = int(os.getenv("RABBITMQ_PORT", 15672))
    rabbitmq_user: str = os.getenv("RABBITMQ_USER")
    rabbitmq_password: str = os.getenv("RABBITMQ_PASSWORD")


settings = Settings()
