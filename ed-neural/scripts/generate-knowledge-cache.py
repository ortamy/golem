#!/usr/bin/env python3
# neural/scripts/generate-knowledge-cache.py — генерация кэша знаний для RAG+CAG
import sys
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_error, print_warning, print_hint,
    REPO_ROOT
)

# Конфигурация
CACHE_DIR = REPO_ROOT / "tools" / "cache" / "neural-cache"
SOURCE_DIRS = ["terminology", "researches", "instructions/exposure"]
CHUNK_SIZE = 500  # символов на чанк
CHUNK_OVERLAP = 100  # перекрытие между чанками
MIN_CHUNK_LENGTH = 100  # короче — не сохраняем
IGNORE_FILES = {"README.md", "STRUCTURE.md", "GLOSSARY.md", "CHANGELOG.md"}


def extract_clean_content(filepath: Path) -> str | None:
    """Извлекает чистый текст из md-файла (без метаданных)."""
    content = read_file_safe(filepath)
    if not content:
        return None

    # Убираем метаданные
    content = re.sub(r'\*\*Метаданные файла\*\*.*?\n---\n', '', content, flags=re.DOTALL)

    # Убираем эмодзи-заголовки но оставляем текст
    content = re.sub(r'^#\s+[\U0001F000-\U0001FFFF]\s*', '# ', content, flags=re.MULTILINE)

    # Убираем навигационные блоки
    content = re.sub(r'<!-- NAVIGATION_START -->.*?<!-- NAVIGATION_END -->', '', content, flags=re.DOTALL)

    # Убираем связанные файлы в конце
    content = re.sub(r'\n---\n\n## 🔗 СВЯЗАННЫЕ.*$', '', content, flags=re.DOTALL)

    return content.strip()


def extract_title(content: str) -> str:
    """Извлекает заголовок H1."""
    match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        # Убираем эмодзи
        title = re.sub(r'[\U0001F000-\U0001FFFF]', '', title).strip()
        return title
    return ""


def extract_topic(content: str) -> str:
    """Извлекает тему из метаданных."""
    match = re.search(r'\*\*Тема:\*\*\s*(.+?)(?:\n|$)', content)
    return match.group(1).strip() if match else ""


def chunk_text(text: str, title: str, topic: str, filepath: str) -> list:
    """Разбивает текст на чанки с перекрытием."""
    chunks = []
    words = text.split()
    chunk_words = []

    for word in words:
        chunk_words.append(word)
        if len(' '.join(chunk_words)) >= CHUNK_SIZE:
            chunk_text = ' '.join(chunk_words)
            chunk_id = hashlib.md5(chunk_text.encode()).hexdigest()[:12]
            chunks.append({
                "id": chunk_id,
                "file": filepath,
                "title": title,
                "topic": topic,
                "text": chunk_text,
                "length": len(chunk_text),
            })
            # Перекрытие
            overlap_words = chunk_words[-int(CHUNK_OVERLAP / 5):] if len(chunk_words) > 20 else []
            chunk_words = overlap_words

    # Последний чанк
    if chunk_words and len(' '.join(chunk_words)) >= MIN_CHUNK_LENGTH:
        chunk_text = ' '.join(chunk_words)
        chunk_id = hashlib.md5(chunk_text.encode()).hexdigest()[:12]
        chunks.append({
            "id": chunk_id,
            "file": filepath,
            "title": title,
            "topic": topic,
            "text": chunk_text,
            "length": len(chunk_text),
        })

    return chunks


def process_file(filepath: Path) -> list:
    """Обрабатывает один файл и возвращает чанки."""
    content = extract_clean_content(filepath)
    if not content or len(content) < MIN_CHUNK_LENGTH:
        return []

    rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
    title = extract_title(content) or filepath.stem.replace('-', ' ')
    topic = extract_topic(content)

    # Убираем заголовки из текста для чанков
    body = re.sub(r'^#.*$', '', content, flags=re.MULTILINE).strip()

    return chunk_text(body, title, topic, rel_path)


def generate_summary(chunks: list, filepath: str, title: str) -> dict:
    """Генерирует суммарный чанк для файла."""
    # Берём первый и последний чанк + заголовки
    full_text = ' '.join([c["text"][:200] for c in chunks[:2]] + [c["text"][-200:] for c in chunks[-2:]])

    return {
        "id": hashlib.md5((filepath + "_summary").encode()).hexdigest()[:12],
        "file": filepath,
        "title": title,
        "type": "summary",
        "text": full_text,
        "length": len(full_text),
        "chunks_count": len(chunks),
        "total_length": sum(c["length"] for c in chunks),
    }


def main():
    rebuild = "--rebuild" in sys.argv

    print_header("ГЕНЕРАЦИЯ КЭША ЗНАНИЙ", "🧠")

    if rebuild and CACHE_DIR.exists():
        import shutil
        shutil.rmtree(CACHE_DIR)
        print("🗑️ Старый кэш удалён")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Собираем все файлы
    all_files = []
    for sd in SOURCE_DIRS:
        dp = REPO_ROOT / sd
        if dp.exists():
            all_files.extend(sorted(dp.rglob("*.md")))

    all_files = [f for f in all_files if f.name not in IGNORE_FILES]
    total = len(all_files)

    print(f"📁 Файлов для обработки: {total}")
    print(f"📏 Размер чанка: {CHUNK_SIZE} символов")
    print(f"🔄 Перекрытие: {CHUNK_OVERLAP} символов")

    all_chunks = []
    summaries = []
    stats = {
        "files_processed": 0,
        "files_skipped": 0,
        "total_chunks": 0,
        "total_chars": 0,
        "date": datetime.now().isoformat(),
        "source_dirs": SOURCE_DIRS,
        "chunk_size": CHUNK_SIZE,
    }

    for i, fp in enumerate(all_files, 1):
        chunks = process_file(fp)
        if chunks:
            all_chunks.extend(chunks)
            stats["files_processed"] += 1
            stats["total_chunks"] += len(chunks)
            stats["total_chars"] += sum(c["length"] for c in chunks)

            # Суммари
            rel_path = str(fp.relative_to(REPO_ROOT)).replace('\\', '/')
            title = chunks[0]["title"]
            summary = generate_summary(chunks, rel_path, title)
            summaries.append(summary)
        else:
            stats["files_skipped"] += 1

        progress_bar(i, total, extra=f"чанков: {stats['total_chunks']}")

    finish_progress()

    # Сохраняем чанки
    chunks_file = CACHE_DIR / "knowledge-chunks.json"
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump({"stats": stats, "chunks": all_chunks}, f, ensure_ascii=False, indent=2)

    # Сохраняем суммари
    summaries_file = CACHE_DIR / "knowledge-summaries.json"
    with open(summaries_file, 'w', encoding='utf-8') as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    # Сохраняем индекс (для быстрого поиска по файлам и ключевым словам)
    index = {}
    for c in all_chunks:
        key = c["file"]
        if key not in index:
            index[key] = {"title": c["title"], "topic": c.get("topic", ""), "chunk_ids": []}
        index[key]["chunk_ids"].append(c["id"])

    index_file = CACHE_DIR / "knowledge-index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    # Вывод статистики
    print(f"\n📊 СТАТИСТИКА:")
    print(f"  Файлов обработано: {stats['files_processed']}")
    print(f"  Файлов пропущено: {stats['files_skipped']}")
    print(f"  Всего чанков: {stats['total_chunks']}")
    print(f"  Всего символов: {stats['total_chars']:,}")
    print(f"  Суммари: {len(summaries)}")
    print(f"  Записей в индексе: {len(index)}")

    # Размеры файлов
    for f in [chunks_file, summaries_file, index_file]:
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name}: {size_kb:.0f} КБ")

    print_success(f"\n✅ Кэш сохранён в {CACHE_DIR}")
    print_hint("Для использования: python neural/inference/client.py --use-cache")

    return 0


if __name__ == "__main__":
    sys.exit(main())