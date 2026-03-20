# -*- coding: utf-8 -*-

.PHONY: help install run prod build up down logs clean clean-py fix check

# --- Конфигурация ---
COMPOSE := docker compose
PORT := 14101

# --- Команды ---

help:
	@echo "RabbitMQ Health API - доступные команды:"
	@echo ""
	@echo "  make install       - Установить все зависимости (uv)"
	@echo "  make run           - Запуск локального сервера с reload"
	@echo "  make prod          - Запуск production сервера"
	@echo "  make build         - Сборка Docker-образа"
	@echo "  make up            - Запуск в Docker (фоновый режим)"
	@echo "  make down          - Остановка Docker-контейнеров"
	@echo "  make logs          - Просмотр логов Docker"
	@echo "  make clean         - Остановка и удаление контейнеров, volumes"
	@echo "  make clean-py      - Очистка Python-кэша"
	@echo ""
	@echo "  make fix           - Форматирование кода (black)"
	@echo "  make check         - Проверка форматирования (black --check)"

install:
	@echo "📦 Установка зависимостей (uv)..."
	uv sync --all-extras --dev

run:
	@echo "🚀 Запуск локального сервера с reload на порту $(PORT)..."
	uv run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $(PORT)

prod:
	@echo "🚀 Запуск production сервера на порту $(PORT)..."
	uv run python -m uvicorn app.main:app --host 0.0.0.0 --port $(PORT)

build:
	@echo "🐳 Сборка Docker-образа..."
	$(COMPOSE) build

up:
	@echo "🐳 Запуск в Docker (фоновый режим)..."
	$(COMPOSE) up -d

down:
	@echo "🛑 Остановка Docker-контейнеров..."
	$(COMPOSE) down

logs:
	@echo "📋 Просмотр логов Docker..."
	$(COMPOSE) logs -f

clean:
	@echo "🧹 Остановка и удаление контейнеров, volumes..."
	$(COMPOSE) down -v

clean-py:
	@echo "🧹 Очистка Python-кэша..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# --- Code Quality (black) ---

fix:
	@echo "✨ Форматирование кода (black)..."
	uv run black .

check:
	@echo "🔍 Проверка форматирования (black --check)..."
	uv run black . --check
