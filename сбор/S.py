#!/usr/bin/env python3
"""
PyPI Docs Downloader & SQLite Saver
Скачивает метаданные библиотек из PyPI и сохраняет в локальную БД.
Позже можно расширить для парсинга реальной документации и векторизации.
"""

import os
import sys
import json
import time
import sqlite3
import requests
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

# ==================== CONFIG ====================
PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"
PYPI_BASE_URL = "https://pypi.org/project/{package}/"
REQUESTS_TIMEOUT = 15
RATE_LIMIT_DELAY = 0.5  # секунды между запросами (чтобы не получить 429)
MAX_RETRIES = 3
DB_FILENAME = "pypi_docs.db"
LOG_FILE = "pypi_downloader.log"

# Поля, которые будем сохранять из PyPI JSON
FIELDS_TO_SAVE = [
    "name", "version", "summary", "description", "description_content_type",
    "home_page", "project_urls", "author", "author_email", "maintainer",
    "maintainer_email", "license", "keywords", "classifiers", "requires_python",
    "requires_dist", "docs_url", "downloaded_at"
]
# ===============================================

def setup_logger():
    """Простой логгер в файл + консоль"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8", mode="a"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()

def init_db(db_path: str) -> sqlite3.Connection:
    """Создаёт таблицу, если её нет"""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")  # лучше для конкурентного доступа
    conn.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            version TEXT,
            summary TEXT,
            description TEXT,
            description_content_type TEXT,
            home_page TEXT,
            project_urls TEXT,  -- JSON-строка
            author TEXT,
            author_email TEXT,
            maintainer TEXT,
            maintainer_email TEXT,
            license TEXT,
            keywords TEXT,
            classifiers TEXT,  -- JSON-строка списка
            requires_python TEXT,
            requires_dist TEXT,  -- JSON-строка списка
            docs_url TEXT,
            downloaded_at TEXT,
            raw_json TEXT,  -- полный ответ на всякий случай
            error_message TEXT,
            retry_count INTEGER DEFAULT 0
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON packages(name)")
    conn.commit()
    return conn

def parse_requirements(req_file: str) -> List[Dict[str, str]]:
    """Парсит requirements.txt в список {name, version}"""
    packages = []
    with open(req_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            # Обработка git-ссылок, локальных путей и т.д.
            if line.startswith("git+") or line.startswith("http") or line.startswith("./"):
                logger.warning(f"Пропускаю сложный пакет: {line}")
                continue
            # Разбор name==version, name>=version, name и т.д.
            for sep in ["==", ">=", "<=", ">", "<", "~=", "!="]:
                if sep in line:
                    name, version = line.split(sep, 1)
                    packages.append({"name": name.strip().lower(), "version": version.strip()})
                    break
            else:
                # Просто имя без версии
                packages.append({"name": line.lower(), "version": None})
    return packages

def fetch_pypi_metadata(package_name: str, session: requests.Session) -> Optional[Dict]:
    """Запрашивает метаданные из PyPI JSON API с повторами"""
    url = PYPI_JSON_URL.format(package=package_name)
    for attempt in range(MAX_RETRIES):
        try:
            resp = session.get(url, timeout=REQUESTS_TIMEOUT)
            if resp.status_code == 404:
                logger.warning(f"Пакет не найден на PyPI: {package_name}")
                return None
            resp.raise_for_status()
            data = resp.json()
            # Извлекаем полезную информацию
            info = data.get("info", {})
            urls = info.get("project_urls") or {}
            # Пытаемся найти docs URL
            docs_url = None
            for key in ["Documentation", "Docs", "ReadTheDocs", "docs"]:
                if key.lower() in {k.lower() for k in urls}:
                    docs_url = next((v for k, v in urls.items() if k.lower() == key.lower()), None)
                    break
            if not docs_url and "homepage" in urls:
                docs_url = urls["homepage"]
            
            return {
                "name": info.get("name", package_name),
                "version": info.get("version"),
                "summary": info.get("summary"),
                "description": info.get("description"),
                "description_content_type": info.get("description_content_type"),
                "home_page": info.get("home_page"),
                "project_urls": json.dumps(urls, ensure_ascii=False) if urls else None,
                "author": info.get("author"),
                "author_email": info.get("author_email"),
                "maintainer": info.get("maintainer"),
                "maintainer_email": info.get("maintainer_email"),
                "license": info.get("license"),
                "keywords": info.get("keywords"),
                "classifiers": json.dumps(info.get("classifiers", []), ensure_ascii=False),
                "requires_python": info.get("requires_python"),
                "requires_dist": json.dumps(info.get("requires_dist", []), ensure_ascii=False) if info.get("requires_dist") else None,
                "docs_url": docs_url,
                "downloaded_at": datetime.now().isoformat(),
                "raw_json": json.dumps(data, ensure_ascii=False)
            }
        except requests.exceptions.RequestException as e:
            logger.warning(f"Попытка {attempt+1}/{MAX_RETRIES} для {package_name}: {e}")
            time.sleep(2 ** attempt)  # экспоненциальная задержка
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error для {package_name}: {e}")
            return None
    logger.error(f"Не удалось получить данные для {package_name} после {MAX_RETRIES} попыток")
    return None

def save_to_db(conn: sqlite3.Connection, data: Dict, error: Optional[str] = None):
    """Сохраняет или обновляет запись в БД (UPSERT)"""
    cursor = conn.cursor()
    # Проверяем, есть ли уже запись
    cursor.execute("SELECT id, retry_count FROM packages WHERE name = ?", (data["name"],))
    existing = cursor.fetchone()
    
    if existing:
        pkg_id, retry_count = existing
        if error:
            # Обновляем только ошибку и счётчик попыток
            cursor.execute("""
                UPDATE packages SET error_message = ?, retry_count = retry_count + 1, downloaded_at = ?
                WHERE id = ?
            """, (error, datetime.now().isoformat(), pkg_id))
        else:
            # Полное обновление
            cursor.execute(f"""
                UPDATE packages SET 
                    {", ".join(f"{f} = ?" for f in FIELDS_TO_SAVE if f not in ["name", "raw_json"])},
                    raw_json = ?, error_message = NULL, retry_count = 0
                WHERE id = ?
            """, [data.get(f) for f in FIELDS_TO_SAVE if f not in ["name", "raw_json"]] + [data["raw_json"], None, pkg_id])
    else:
        # Вставка новой записи
        placeholders = ", ".join("?" for _ in FIELDS_TO_SAVE + ["raw_json", "error_message", "retry_count"])
        cursor.execute(f"""
            INSERT INTO packages ({", ".join(FIELDS_TO_SAVE + ["raw_json", "error_message", "retry_count"])})
            VALUES ({placeholders})
        """, [data.get(f) for f in FIELDS_TO_SAVE] + [data["raw_json"], error, 0])
    
    conn.commit()

def main():
    parser = argparse.ArgumentParser(description="Скачивает метаданные пакетов из PyPI в SQLite")
    parser.add_argument("-r", "--requirements", type=str, default="requirements.txt",
                        help="Путь к requirements.txt")
    parser.add_argument("-d", "--database", type=str, default=DB_FILENAME,
                        help="Путь к SQLite БД")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Перезаписать даже успешные записи")
    parser.add_argument("-s", "--skip", type=str, nargs="*",
                        help="Пропустить указанные пакеты")
    parser.add_argument("-l", "--limit", type=int, default=0,
                        help="Обработать только первые N пакетов (0 = все)")
    args = parser.parse_args()

    if not os.path.exists(args.requirements):
        logger.error(f"Файл не найден: {args.requirements}")
        sys.exit(1)

    packages = parse_requirements(args.requirements)
    if args.skip:
        packages = [p for p in packages if p["name"] not in [s.lower() for s in args.skip]]
    if args.limit > 0:
        packages = packages[:args.limit]

    logger.info(f"Загружено {len(packages)} пакетов из {args.requirements}")
    conn = init_db(args.database)
    session = requests.Session()
    session.headers.update({"User-Agent": "PyPI-Downloader/1.0 (+https://pypi.org)"})

    success_count = 0
    error_count = 0
    skip_count = 0

    for i, pkg in enumerate(packages, 1):
        name = pkg["name"]
        version = pkg["version"]
        
        # Проверяем, есть ли уже успешная запись
        if not args.force:
            cursor = conn.cursor()
            cursor.execute("SELECT id, error_message FROM packages WHERE name = ?", (name,))
            existing = cursor.fetchone()
            if existing and existing[1] is None:  # есть и без ошибки
                logger.info(f"[{i}/{len(packages)}] Пропускаю (уже есть): {name}")
                skip_count += 1
                continue

        logger.info(f"[{i}/{len(packages)}] Обрабатываю: {name}{'==' + version if version else ''}")
        
        metadata = fetch_pypi_metadata(name, session)
        
        if metadata:
            save_to_db(conn, metadata)
            logger.info(f"✓ Сохранено: {name} ({metadata['version']})")
            success_count += 1
        else:
            # Сохраняем запись с ошибкой, чтобы не пытаться снова без --force
            placeholder = {"name": name, "version": version, "raw_json": None}
            for f in FIELDS_TO_SAVE:
                if f not in placeholder:
                    placeholder[f] = None
            save_to_db(conn, placeholder, error="Failed to fetch metadata")
            logger.error(f"✗ Ошибка: {name}")
            error_count += 1
        
        time.sleep(RATE_LIMIT_DELAY)

    conn.close()
    logger.info(f"\n=== Готово ===\nУспешно: {success_count}\nОшибки: {error_count}\nПропущено: {skip_count}\nБаза: {args.database}")

if __name__ == "__main__":
    main()
