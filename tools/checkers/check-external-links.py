#!/usr/bin/env python3
# tools/checkers/validate-external-links.py — проверка внешних HTTP-ссылок
import sys
import re
import urllib.request
import urllib.error
import ssl
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_error, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions", "docs", "ideas"]
TIMEOUT = 5  # секунд на запрос
IGNORE_DOMAINS = {"localhost", "127.0.0.1", "example.com"}


def extract_external_links(content: str) -> list:
    """Извлекает все внешние HTTP(S) ссылки из текста."""
    links = []
    # Markdown: [текст](url)
    for match in re.finditer(r'\[([^\]]*)\]\((https?://[^\)]+)\)', content):
        links.append(match.group(2))
    # Голые URL
    for match in re.finditer(r'(?<!\()https?://[^\s\)\[\]]+', content):
        links.append(match.group())
    return links


def check_link(url: str) -> tuple:
    """Проверяет одну ссылку. Возвращает (url, статус, код)."""
    # Пропускаем игнорируемые домены
    for domain in IGNORE_DOMAINS:
        if domain in url:
            return url, "пропущен", 0

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 Golem-Project/3.0'
        })
        response = urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx)
        return url, "OK", response.getcode()
    except urllib.error.HTTPError as e:
        return url, f"HTTP {e.code}", e.code
    except urllib.error.URLError as e:
        return url, "нет соединения", 0
    except Exception as e:
        return url, f"ошибка: {str(e)[:50]}", 0


def main():
    print_header("ПРОВЕРКА ВНЕШНИХ ССЫЛОК", "🌐")

    # Собираем все ссылки
    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total_files = len(all_files)
    print(f"Файлов для проверки: {total_files}")

    # Извлекаем ссылки
    file_links = {}
    all_links = set()

    for filepath in all_files:
        content = read_file_safe(filepath)
        if not content:
            continue
        links = extract_external_links(content)
        if links:
            rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
            file_links[rel_path] = links
            all_links.update(links)

    unique_links = list(all_links)
    total_links = len(unique_links)

    if total_links == 0:
        print_success("Внешних ссылок не найдено")
        return 0

    print(f"Уникальных ссылок: {total_links}")
    print(f"Файлов со ссылками: {len(file_links)}")
    print(f"Проверка (таймаут: {TIMEOUT}с)...\n")

    # Проверяем ссылки
    results = {"OK": [], "пропущен": [], "ошибки": []}

    for i, url in enumerate(unique_links, 1):
        _, status, code = check_link(url)

        if status == "OK":
            results["OK"].append((url, code))
        elif status == "пропущен":
            results["пропущен"].append((url, 0))
        else:
            results["ошибки"].append((url, status))

        progress_bar(i, total_links, extra=f"OK: {len(results['OK'])} | ошибок: {len(results['ошибки'])}")

    finish_progress()

    # Результаты
    print(f"\n✅ Успешно: {len(results['OK'])}")
    print(f"⏭️ Пропущено: {len(results['пропущен'])}")
    print(f"❌ Ошибок: {len(results['ошибки'])}")

    if results["ошибки"]:
        print_error(f"НЕДОСТУПНЫЕ ССЫЛКИ:")
        for url, error in results["ошибки"][:20]:
            # Находим файлы, где эта ссылка
            sources = [f for f, links in file_links.items() if url in links]
            source_str = sources[0] if sources else "неизвестно"
            print(f"   • [{error}] {url}")
            print(f"     в файле: {source_str}")

        if len(results["ошибки"]) > 20:
            print(f"   ... и ещё {len(results['ошибки']) - 20}")

    if results["ошибки"]:
        return 1
    else:
        print_success("Все внешние ссылки доступны")
        return 0


if __name__ == "__main__":
    sys.exit(main())

