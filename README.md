# RabbitMQ Health API

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-async-success)
![Docker](https://img.shields.io/badge/docker-ready-blue)

Лёгкий внутренний HTTP‑сервис для мониторинга **RabbitMQ** и состояния **виртуальной машины**, предназначенный для использования за Cloudflare Tunnel (или другим reverse‑proxy) без публикации брокера наружу.

Проект ориентирован на:
- Uptime Kuma (HTTP‑healthcheck)
- ручную диагностику состояния RabbitMQ
- минимальный оверхед и простоту развёртывания

---

## 📑 Содержание

1. [Назначение проекта](#назначение-проекта)
2. [Архитектура и идея](#архитектура-и-идея)
3. [Эндпоинты API](#эндпоинты-api)
4. [Важно про пути и .env](#важно-про-пути-и-env)
5. [Стек технологий](#стек-технологий)
6. [Запуск проекта](#запуск-проекта)
7. [Docker и docker-compose](#docker-и-docker-compose)
8. [Логирование](#логирование)
9. [Безопасность](#безопасность)

---

## Назначение проекта

**RabbitMQ Health API** решает сразу несколько задач:

- 🔒 RabbitMQ и Management UI **не открываются наружу**
- ❤️ Даёт простой HTTP‑endpoint для Uptime Kuma
- 📊 Позволяет посмотреть загрузку брокера (очереди, сообщения, подключения)
- 🖥️ Показывает базовые метрики ВМ (CPU / RAM / Disk)

Сервис разворачивается рядом с RabbitMQ и общается с ним **локально** через Management API.

---

## Архитектура и идея

```
Uptime Kuma / Browser
        │  HTTPS
        ▼
RabbitMQ Health API (FastAPI)
        │  localhost
        ▼
RabbitMQ Management API (15672)
```

- AMQP (`5672`) и Management UI (`15672`) **не публикуются**
- наружу доступен только HTTP‑API
- идеально подходит для Cloudflare Tunnel

---

## Эндпоинты API

⚠️ Все пути ниже приведены **для примера**. Реальный путь зависит от значения `API_BASE_PATH` в `.env`.

### `/health`

```
GET http://localhost:8000/api/rabbitmq/health
```

**Назначение:**
- основной healthcheck для Uptime Kuma
- быстрый и лёгкий

**Что показывает:**
- общее количество сообщений во всех очередях
- количество подключений
- относительную загрузку брокера
- цветовой уровень состояния

Пример ответа:

```json
{
  "messages": 124,
  "connections": 5,
  "load_percent": 62.0,
  "level": "🟡"
}
```

Цветовая индикация:
- 🟢 `green` — до 50%
- 🟡 `yellow` — 51–75%
- 🔴 `red` — 76% и выше

---

### `/status`

```
GET http://localhost:8000/api/rabbitmq/status
```

**Назначение:**
- ручная диагностика состояния RabbitMQ

**Что можно узнать:**
- версию RabbitMQ
- uptime ноды
- список очередей
- количество сообщений
- количество консьюмеров
- общее число подключений

Используется **по необходимости**, а не для частого опроса.

---

### `/metrics`

```
GET http://localhost:8000/api/rabbitmq/metrics
```

**Назначение:**
- быстрый просмотр состояния ВМ

**Что показывает:**
- загрузку CPU
- использование памяти
- использование диска

Без Prometheus, в простом JSON‑виде — удобно для человека.

---

### `/docs`

```
GET http://localhost:8000/docs
```

Интерактивная документация FastAPI (Swagger UI):
- список всех эндпоинтов
- реальные пути с учётом `API_BASE_PATH`
- примеры запросов и ответов

---

## Важно про пути и `.env`

⚠️ **Ключевой момент проекта** — все внешние пути задаются через `.env`.

```env
API_BASE_PATH=/api/rabbitmq
```

Это означает, что:

- при смене значения `API_BASE_PATH`
- **все URL автоматически меняются**

Примеры:

| API_BASE_PATH | Итоговый URL `/health` |
|--------------|------------------------|
| `/api/rabbitmq` | `/api/rabbitmq/health` |
| `/rabbitmq` | `/rabbitmq/health` |

Это позволяет:
- использовать один и тот же код для dev / prod
- удобно проксировать через Cloudflare Tunnel

---

## Стек технологий

- **Python 3.13+**
- **FastAPI** — HTTP API
- **httpx** — запросы к RabbitMQ Management API
- **psutil** — метрики ВМ
- **pydantic-settings** — управление настройками
- **uv** — управление зависимостями
- **Docker / Docker Compose** — развёртывание

---

## Запуск проекта

### Локальная разработка

```bash
# Установка зависимостей
make install

# Запуск сервера с автоперезагрузкой
make run
```

Или вручную:

```bash
uv venv
source .venv/bin/activate
uv sync
uvicorn app.main:app --reload
```

### Production запуск

```bash
make prod
```

---

## Docker и docker-compose

### Быстрый старт

```bash
# Сборка образа
make build

# Запуск контейнеров
make up

# Просмотр логов
make logs

# Остановка
make down
```

### Вручную

```bash
docker compose build
docker compose up -d
```

После запуска:

- `http://localhost:14101/api/rabbitmq/health`
- `http://localhost:14101/api/rabbitmq/status`
- `http://localhost:14101/api/rabbitmq/metrics`

---

## Логирование

Приложение использует централизованную систему логирования с поддержкой нескольких приёмников.

### Настройка

Параметры логирования задаются в `.env`:

```env
# Логирование
LOG_DIR="logs"
LOG_FILE="app.log"
LOG_JSON_FILE="app.json"

LOG_TO_FILE=True
LOG_TO_CONSOLE=True
LOG_TO_JSON=False

LOG_ROTATION="50 MB"
LOG_RETENTION="30 days"

LOG_LEVEL_FILE="INFO"
LOG_LEVEL_CONSOLE="INFO"
```

### Особенности

- **Фильтрация чувствительных данных** — пароли и токены автоматически скрываются
- **Ротация логов** — старые файлы архивируются и удаляются
- **Асинхронная запись** — не блокирует работу приложения
- **JSON формат** — опционально для удобного парсинга

Логи сохраняются в папку `logs/` (по умолчанию).

---

## Безопасность

- используется отдельный пользователь RabbitMQ: `monitoring`
- права: **read-only**
- Management API доступен **только локально**
- наружу публикуется только HTTP‑сервис

Планы на будущее:
- [ ] закрыть `/status` и `/metrics` токеном

---

## Лицензия

Проект распространяется под лицензией **MIT**.

* * *

### Как можно отблагодарить:
* Оформить удобную для вас подписку на [Boosty.to](https://boosty.to/lliammah/ref)
* Разово поддержать через [DonationAlerts](https://www.donationalerts.com/r/lliammah)
