# -*- coding: utf-8 -*-

.PHONY: help install local prod down logs clean clean-py fix check check-env test-context

# --- Конфигурация ---
COMPOSE := docker compose
PORT := 14101
UV := uv
TEST_CONTEXT := docker build --no-cache --progress=plain -t test-context .

# --- Переменные окружения для uv ---
export UV_LINK_MODE := copy

# --- Команды ---

help:
	@echo "RabbitMQ Health API - доступные команды:"
	@echo ""
	@echo "  make install       - Установить зависимости (uv)"
	@echo "  make local         - Запуск на хосте (uvicorn + reload)"
	@echo "  make prod          - Запуск в Docker (production)"
	@echo "  make down          - Остановка Docker-контейнеров"
	@echo "  make clean         - Остановка и удаление контейнеров, volumes"
	@echo "  make clean-py      - Очистка Python-кэша"
	@echo ""
	@echo "  make fix           - Форматирование и исправление кода"
	@echo "  make check         - Проверка кода (ruff + pyright)"
	@echo "  make check-env     - Сверка .env с .env.template"
	@echo "  make test-context  - Проверка контекста Docker-сборки"

install:
	@echo "📦 Установка зависимостей..."
	$(UV) sync --all-extras --dev

local:
	@echo "🚀 Запуск на хосте (uvicorn + reload)..."
	$(UV) run python -m uvicorn app.main:app --host 0.0.0.0 --port $(PORT) --reload

prod:
	@echo "🐳 Запуск в Docker (с пересборкой)..."
	$(COMPOSE) up -d --build

down:
	@echo "🛑 Остановка контейнеров..."
	$(COMPOSE) down

logs:
	@echo "📋 Логи Docker..."
	$(COMPOSE) logs -f

clean:
	@echo "🧹 Остановка и удаление контейнеров, volumes..."
	$(COMPOSE) down -v

clean-py:
	@echo "🧹 Очистка Python-кэша..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# --- Code Quality ---

fix:
	@echo "✨ Форматирование и исправление кода..."
	$(UV) run ruff check . --fix
	$(UV) run black .

check:
	@echo "🔍 Проверка кода (ruff + pyright)..."
	$(UV) run ruff check .
	$(UV) run pyright
	$(UV) run black . --check

check-env:
	@echo "🔍 Сверяю .env с .env.template..."
	@uv run python scripts/check_env.py

test-context:
	@echo "🛠️ Проверка контекста Docker-сборки..."
	$(TEST_CONTEXT)
