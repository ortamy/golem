#!/usr/bin/env python3
# tools/generators/generate-training-data.py — создание датасета для нейросети «Эд»
import sys
import re
import json
from pathlib import Path
# from datetime import datetime  # TODO: проверить, используется ли

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_hint, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions/exposure"]
OUTPUT_FILE = REPO_ROOT / "neural" / "training-data" / "qa-pairs.json"


def extract_title(content: str) -> str:
    """Извлекает заголовок."""
    match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_topic(content: str) -> str:
    """Извлекает тему из метаданных."""
    match = re.search(r'[-*]\s*\*\*Тема:\*\*\s*(.+?)(?:\n|$)', content)
    return match.group(1).strip() if match else ""


def extract_body(content: str) -> str:
    """Извлекает тело файла (без метаданных и заголовка)."""
    if '**Метаданные файла**' in content:
        start = content.find('**Метаданные файла**')
        rest = content[start:]
        end_match = re.search(r'\n---|\n# |\n## ', rest[30:])
        if end_match:
            content = content[:start] + rest[30 + end_match.start():]
    # Убираем первый заголовок
    content = re.sub(r'^#\s+.+$', '', content, flags=re.MULTILINE).strip()
    return content


def extract_quotes(content: str) -> list:
    """Извлекает цитаты из ТаНаХа."""
    quotes = []
    for match in re.finditer(r'>\s*(.+?)(?:\n|$)', content):
        text = match.group(1).strip()
        if len(text) > 20 and ('Яхве' in text or 'יהוה' in text or 'ТаНаХ' in text or 'Тора' in text or 'сказал' in text.lower()):
            quotes.append(text)
    return quotes[:3]


def extract_keywords(content: str) -> str:
    """Извлекает ключевые ивритские слова."""
    words = re.findall(r'([א-ת]+(?:\s+[א-ת]+)?)', content)
    unique = list(set(words))[:5]
    return ', '.join(unique) if unique else ""


def generate_questions(title: str, topic: str, body: str, quotes: list) -> list:
    """Генерирует вопросы и ответы на основе файла."""
    qa_pairs = []

    # Вопрос 1: Что это?
    if title:
        qa_pairs.append({
            "question": f"Что такое {title.lower()}?",
            "answer": f"{title} — {topic}" if topic else f"Исследование на тему: {title[:200]}"
        })

    # Вопрос 2: Что говорит ТаНаХ?
    if quotes:
        qa_pairs.append({
            "question": f"Что говорит ТаНаХ о {title.lower()}?",
            "answer": quotes[0][:500]
        })

    # Вопрос 3: В чём суть?
    first_paragraph = body[:500].strip()
    if first_paragraph:
        qa_pairs.append({
            "question": f"В чём суть {title.lower()}?",
            "answer": first_paragraph
        })

    # Вопрос 4: Почему это важно?
    if len(body) > 500:
        qa_pairs.append({
            "question": f"Почему важно понимать {title.lower()}?",
            "answer": body[500:1000].strip()[:500]
        })

    # Вопрос 5: Как это связано с Яхве?
    if 'Яхве' in body or 'יהוה' in body:
        qa_pairs.append({
            "question": f"Как {title.lower()} связано с Яхве?",
            "answer": f"В исследовании «{title}» раскрывается, что {topic.lower() if topic else title.lower()} напрямую связано с замыслом Яхве. {body[:300]}"
        })

    return qa_pairs


def main():
    print_header("ГЕНЕРАЦИЯ ТРЕНИРОВОЧНЫХ ДАННЫХ", "🧠")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    print(f"Найдено файлов: {total}")

    all_pairs = []
    stats = {"files_processed": 0, "pairs_generated": 0}

    for i, filepath in enumerate(all_files, 1):
        content = read_file_safe(filepath)
        if not content:
            continue

        title = extract_title(content)
        topic = extract_topic(content)
        body = extract_body(content)
        quotes = extract_quotes(content)

        if not title or not body:
            continue

        pairs = generate_questions(title, topic, body, quotes)
        all_pairs.extend(pairs)
        stats["files_processed"] += 1
        stats["pairs_generated"] += len(pairs)

        progress_bar(i, total, extra=f"файлов: {stats['files_processed']} | пар: {stats['pairs_generated']}")

    finish_progress()

    # Сохраняем
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_pairs, f, ensure_ascii=False, indent=2)

    print(f"\n📊 Статистика:")
    print(f"   Обработано файлов: {stats['files_processed']}")
    print(f"   Сгенерировано пар: {stats['pairs_generated']}")
    print(f"   Сохранено в: {OUTPUT_FILE}")

    # Пример
    if all_pairs:
        print(f"\n📋 Пример пары:")
        print(f"   Q: {all_pairs[0]['question']}")
        print(f"   A: {all_pairs[0]['answer'][:150]}...")

    print_hint("Файл готов для fine-tuning модели «Эд»")
    return 0


if __name__ == "__main__":
    sys.exit(main())

