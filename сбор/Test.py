#!/usr/bin/env python3
"""
PyPI DB Reader
Чтение, поиск и экспорт данных из SQLite базы, созданной pypi_downloader.py
"""

import os
import sys
import json
import csv
import sqlite3
import argparse
from typing import Optional, List, Dict
from datetime import datetime

# ==================== CONFIG ====================
DEFAULT_DB = "pypi_docs.db"
RESULTS_PER_PAGE = 20
# ===============================================

def connect_db(db_path: str) -> sqlite3.Connection:
    """Подключение к БД с проверкой существования"""
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        print("💡 Сначала запустите pypi_downloader.py для создания базы")
        sys.exit(1)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # доступ к полям по имени
    return conn

def get_stats(conn: sqlite3.Connection) -> Dict:
    """Статистика по базе"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM packages")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM packages WHERE error_message IS NULL")
    success = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM packages WHERE error_message IS NOT NULL")
    errors = cursor.fetchone()[0]
    cursor.execute("SELECT MIN(downloaded_at), MAX(downloaded_at) FROM packages WHERE downloaded_at IS NOT NULL")
    dates = cursor.fetchone()
    return {
        "total": total,
        "success": success,
        "errors": errors,
        "first_download": dates[0],
        "last_download": dates[1]
    }

def list_packages(conn: sqlite3.Connection, 
                  limit: int = RESULTS_PER_PAGE, 
                  offset: int = 0,
                  only_success: bool = True,
                  search: Optional[str] = None) -> List[sqlite3.Row]:
    """Получение списка пакетов с фильтрацией"""
    cursor = conn.cursor()
    query = "SELECT * FROM packages WHERE 1=1"
    params = []
    
    if only_success:
        query += " AND error_message IS NULL"
    
    if search:
        query += " AND (name LIKE ? OR summary LIKE ? OR keywords LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])
    
    query += " ORDER BY name LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    return cursor.fetchall()

def get_package(conn: sqlite3.Connection, name: str) -> Optional[sqlite3.Row]:
    """Получение полной информации по одному пакету"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM packages WHERE name = ?", (name.lower(),))
    return cursor.fetchone()

def search_by_keyword(conn: sqlite3.Connection, keyword: str) -> List[sqlite3.Row]:
    """Поиск пакетов по ключевому слову в классификаторах или зависимостях"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, summary, keywords, classifiers 
        FROM packages 
        WHERE error_message IS NULL 
        AND (
            keywords LIKE ? OR 
            classifiers LIKE ? OR 
            requires_dist LIKE ?
        )
        ORDER BY name
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    return cursor.fetchall()

def export_to_json(conn: sqlite3.Connection, output_file: str, only_success: bool = True):
    """Экспорт всех записей в JSON"""
    cursor = conn.cursor()
    query = "SELECT * FROM packages"
    if only_success:
        query += " WHERE error_message IS NULL"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Конвертируем sqlite3.Row в dict
    result = [dict(row) for row in rows]
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Экспортировано {len(result)} записей в {output_file}")

def export_to_csv(conn: sqlite3.Connection, output_file: str, only_success: bool = True):
    """Экспорт в CSV (без поля raw_json для компактности)"""
    cursor = conn.cursor()
    query = "SELECT * FROM packages"
    if only_success:
        query += " WHERE error_message IS NULL"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    if not rows:
        print("⚠ Нет данных для экспорта")
        return
    
    # Исключаем raw_json из CSV (слишком большой)
    fieldnames = [key for key in rows[0].keys() if key != "raw_json"]
    
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))
    
    print(f"✓ Экспортировано {len(rows)} записей в {output_file}")

def prepare_for_rag(conn: sqlite3.Connection, output_file: str, chunk_size: int = 500):
    """
    Подготовка данных для RAG: создание чанков текста из описаний
    Формат: список словарей {text, metadata}
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name, version, summary, description, docs_url, keywords FROM packages WHERE error_message IS NULL")
    rows = cursor.fetchall()
    
    chunks = []
    for row in rows:
        # Формируем базовый текст
        text_parts = [
            f"Библиотека: {row['name']}",
            f"Версия: {row['version'] or 'N/A'}",
        ]
        if row['summary']:
            text_parts.append(f"Кратко: {row['summary']}")
        if row['description']:
            # Очищаем описание от markdown-разметки (базово)
            desc_clean = row['description'].replace("```", "").replace("#", "").strip()
            text_parts.append(f"Описание: {desc_clean[:2000]}")  # ограничиваем длину
        if row['docs_url']:
            text_parts.append(f"Документация: {row['docs_url']}")
        if row['keywords']:
            text_parts.append(f"Ключевые слова: {row['keywords']}")
        
        full_text = "\n".join(text_parts)
        
        # Чанкинг по размеру (с перекрытием 10%)
        overlap = int(chunk_size * 0.1)
        for i in range(0, len(full_text), chunk_size - overlap):
            chunk = full_text[i:i+chunk_size].strip()
            if len(chunk) > 100:  # фильтр слишком коротких
                chunks.append({
                    "text": chunk,
                    "metadata": {
                        "package": row["name"],
                        "version": row["version"],
                        "source": "pypi_docs_db",
                        "chunk_index": len(chunks)
                    }
                })
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Подготовлено {len(chunks)} чанков для RAG в {output_file}")
    return chunks

def print_package(row: sqlite3.Row, show_raw: bool = False):
    """Красивый вывод информации о пакете"""
    print(f"\n{'='*60}")
    print(f"📦 {row['name']} v{row['version'] or '?'}")
    print(f"{'='*60}")
    
    if row['summary']:
        print(f"📝 {row['summary']}")
    
    if row['home_page']:
        print(f"🌐 Homepage: {row['home_page']}")
    if row['docs_url']:
        print(f"📚 Docs: {row['docs_url']}")
    
    if row['author']:
        print(f"👤 Author: {row['author']}{f' <{row['author_email']}>' if row['author_email'] else ''}")
    
    if row['license']:
        print(f"⚖️  License: {row['license']}")
    
    if row['keywords']:
        print(f"🔑 Keywords: {row['keywords']}")
    
    if row['requires_python']:
        print(f"🐍 Requires Python: {row['requires_python']}")
    
    if row['classifiers']:
        classifiers = json.loads(row['classifiers'])
        ml_classifiers = [c for c in classifiers if "Machine Learning" in c or "AI" in c]
        if ml_classifiers:
            print(f"🤖 ML/AI classifiers: {', '.join(ml_classifiers[:3])}")
    
    if row['description'] and not show_raw:
        desc_preview = row['description'][:300].strip()
        if len(row['description']) > 300:
            desc_preview += "..."
        print(f"\n📄 Description preview:\n{desc_preview}")
    
    if row['error_message']:
        print(f"\n❌ Error: {row['error_message']}")
    
    if show_raw and row['raw_json']:
        print(f"\n🔍 Raw JSON (first 500 chars):\n{row['raw_json'][:500]}...")
    
    print(f"⏰ Downloaded: {row['downloaded_at']}")

def interactive_shell(conn: sqlite3.Connection):
    """Простой интерактивный режим"""
    print("\n🔍 PyPI DB Interactive Reader")
    print("Команды: list, search <term>, info <name>, export <json|csv|rag>, stats, quit")
    
    while True:
        try:
            cmd = input("\n> ").strip()
            if not cmd:
                continue
            
            parts = cmd.split(maxsplit=1)
            action = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else None
            
            if action in ["quit", "exit", "q"]:
                break
            
            elif action == "stats":
                stats = get_stats(conn)
                print(f"\n📊 Статистика:")
                print(f"   Всего записей: {stats['total']}")
                print(f"   Успешно: {stats['success']}")
                print(f"   Ошибки: {stats['errors']}")
                if stats['first_download']:
                    print(f"   Период: {stats['first_download'][:10]} — {stats['last_download'][:10]}")
            
            elif action == "list":
                packages = list_packages(conn, limit=RESULTS_PER_PAGE)
                for pkg in packages:
                    status = "✅" if not pkg['error_message'] else "❌"
                    print(f"{status} {pkg['name']} v{pkg['version'] or '?'} — {pkg['summary'] or 'No summary'}")
                print(f"\nПоказано {len(packages)} из ... (используйте search для фильтрации)")
            
            elif action == "search" and arg:
                results = list_packages(conn, search=arg, limit=50)
                if not results:
                    print("⚠ Ничего не найдено")
                    continue
                for pkg in results:
                    print(f"• {pkg['name']} — {pkg['summary'] or 'No summary'}")
                print(f"\nНайдено: {len(results)}")
            
            elif action == "info" and arg:
                pkg = get_package(conn, arg)
                if pkg:
                    print_package(pkg)
                else:
                    print(f"⚠ Пакет '{arg}' не найден в базе")
            
            elif action == "export" and arg:
                if arg == "json":
                    export_to_json(conn, "pypi_export.json")
                elif arg == "csv":
                    export_to_csv(conn, "pypi_export.csv")
                elif arg == "rag":
                    prepare_for_rag(conn, "pypi_rag_chunks.json")
                else:
                    print("⚠ Формат: json | csv | rag")
            
            elif action == "help":
                print("""
Доступные команды:
  list              — показать первые 20 пакетов
  search <term>     — поиск по имени/описанию/ключевым словам
  info <name>       — подробная информация о пакете
  stats             — статистика базы
  export <format>   — экспорт: json, csv, rag (для векторизации)
  help              — эта справка
  quit / exit       — выход
                """)
            else:
                print("⚠ Неизвестная команда. Введите 'help' для справки")
                
        except KeyboardInterrupt:
            print("\n👋 Выход")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Чтение и экспорт данных из PyPI SQLite базы",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  %(prog)s                          # интерактивный режим
  %(prog)s --stats                  # показать статистику
  %(prog)s --list                   # список пакетов
  %(prog)s --search transformers    # поиск по термину
  %(prog)s --info faiss             # информация о пакете
  %(prog)s --export rag             # подготовить чанки для RAG
  %(prog)s --export json -o out.json  # экспорт в JSON
        """
    )
    
    parser.add_argument("-d", "--database", default=DEFAULT_DB,
                        help=f"Путь к базе данных (по умолчанию: {DEFAULT_DB})")
    parser.add_argument("--stats", action="store_true",
                        help="Показать статистику базы")
    parser.add_argument("--list", action="store_true",
                        help="Список пакетов")
    parser.add_argument("--search", type=str, metavar="TERM",
                        help="Поиск по имени/описанию")
    parser.add_argument("--info", type=str, metavar="PACKAGE",
                        help="Подробная информация о пакете")
    parser.add_argument("--export", choices=["json", "csv", "rag"],
                        help="Экспорт данных в указанный формат")
    parser.add_argument("-o", "--output", type=str,
                        help="Имя выходного файла для экспорта")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Запустить интерактивный режим")
    parser.add_argument("--raw", action="store_true",
                        help="Показывать raw JSON в info (для отладки)")
    
    args = parser.parse_args()
    
    conn = connect_db(args.database)
    
    try:
        # Режим командной строки
        if args.stats:
            stats = get_stats(conn)
            print(json.dumps(stats, indent=2, ensure_ascii=False))
            
        elif args.list:
            packages = list_packages(conn, limit=50)
            for pkg in packages:
                status = "✅" if not pkg['error_message'] else "❌"
                print(f"{status} {pkg['name']} v{pkg['version'] or '?'}")
            print(f"\nВсего показано: {len(packages)}")
            
        elif args.search:
            results = list_packages(conn, search=args.search, limit=50)
            if not results:
                print(f"⚠ Ничего не найдено по запросу '{args.search}'")
            else:
                for pkg in results:
                    print(f"• {pkg['name']} — {pkg['summary'] or 'No summary'}")
                print(f"\nНайдено: {len(results)}")
                
        elif args.info:
            pkg = get_package(conn, args.info)
            if pkg:
                print_package(pkg, show_raw=args.raw)
            else:
                print(f"⚠ Пакет '{args.info}' не найден")
                
        elif args.export:
            output = args.output or f"pypi_export.{args.export}"
            if args.export == "json":
                export_to_json(conn, output)
            elif args.export == "csv":
                export_to_csv(conn, output)
            elif args.export == "rag":
                prepare_for_rag(conn, output)
                
        elif args.interactive or not any([args.stats, args.list, args.search, args.info, args.export]):
            interactive_shell(conn)
            
    finally:
        conn.close()

if __name__ == "__main__":
    main()
