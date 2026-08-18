# -*- coding: utf-8 -*-

"""Сверка .env с .env.template.

Перестраивает .env в точном порядке .env.template:
- комментарии, секции и порядок строк берутся из шаблона;
- значения переменных — из текущего .env (для недостающих — значения
  по умолчанию из шаблона);
- лишние активные переменные удаляются.

Если файл нужно изменить, перед записью создаётся резервная копия
.env-YYYYMMDD-HHMMSS.

Запуск: make check-env или python3 scripts/check_env.py
"""

import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
TEMPLATE_FILE = ROOT / ".env.template"

_ASSIGNMENT_RE = re.compile(r"^([A-Za-z0-9_]+)\s*=")


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _is_comment(line: str) -> bool:
    return line.lstrip().startswith("#")


def _key_of(line: str) -> str | None:
    """Имя переменной из строки вида KEY=value, иначе None."""
    if _is_comment(line):
        return None
    match = _ASSIGNMENT_RE.match(line)
    return match.group(1) if match else None


def sync_env(
    env_path: Path,
    template_path: Path,
    *,
    backup: bool = True,
    backup_suffix: str | None = None,
) -> dict[str, list[str] | str | None]:
    """Синхронизировать .env с шаблоном.

    Args:
        env_path: Путь к файлу .env.
        template_path: Путь к файлу .env.template.
        backup: Создавать ли резервную копию перед изменением.
        backup_suffix: Суффикс (дата-время) для имени копии.

    Returns:
        Словарь с отчётом: added, removed, backup (путь к копии или None).

    Raises:
        FileNotFoundError: Если .env или шаблон отсутствуют.
    """
    if not template_path.is_file():
        raise FileNotFoundError(f"Template not found: {template_path}")
    if not env_path.is_file():
        raise FileNotFoundError(
            f"{env_path} not found. Create it from {template_path}"
        )

    env_values: dict[str, str] = {}
    for line in _read_lines(env_path):
        key = _key_of(line)
        if key is not None:
            env_values[key] = line.split("=", 1)[1].strip()

    template_values: dict[str, str] = {}
    new_lines: list[str] = []
    added: list[str] = []

    for line in _read_lines(template_path):
        key = _key_of(line)
        if key is None:
            new_lines.append(line)
            continue
        template_values[key] = line.split("=", 1)[1].strip()
        if key in env_values:
            new_lines.append(f"{key}={env_values[key]}")
        else:
            new_lines.append(line)
            added.append(key)

    removed = [k for k in env_values if k not in template_values]

    old_content = env_path.read_text(encoding="utf-8")
    new_content = "\n".join(new_lines) + "\n"

    if new_content == old_content:
        return {"added": [], "removed": [], "backup": None}

    backup_path: Path | None = None
    if backup:
        timestamp = backup_suffix or datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = Path(str(env_path) + "-" + timestamp)
        backup_path.write_text(old_content, encoding="utf-8")

    env_path.write_text(new_content, encoding="utf-8")

    return {
        "added": added,
        "removed": removed,
        "backup": str(backup_path) if backup_path else None,
    }


def main() -> int:
    env_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ENV_FILE
    template_path = Path(sys.argv[2]) if len(sys.argv) > 2 else TEMPLATE_FILE

    print(f"Проверка {env_path.name} относительно {template_path.name}...")
    try:
        report = sync_env(env_path, template_path)
    except FileNotFoundError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1

    added = report["added"]
    removed = report["removed"]
    backup = report["backup"]

    if not added and not removed and backup is None:
        print("Изменений не требуется — файл актуален.")
        return 0

    if added:
        print(f"Добавлено: {', '.join(added)}")
    if removed:
        print(f"Удалено: {', '.join(removed)}")
    if not added and not removed:
        print("Порядок строк приведён к .env.template.")
    if backup:
        print(f"Резервная копия: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
