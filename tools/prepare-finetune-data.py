#!/usr/bin/env python3
# prepare_finetune_data.py — подготовка датасета для fine-tune модели «Эд»

import os
import re
import json
import random
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TERMINOLOGY_DIR = REPO_ROOT / "terminology"
RESEARCHES_DIR = REPO_ROOT / "researches"
INSTRUCTIONS_DIR = REPO_ROOT / "instructions"
OUTPUT_FILE = REPO_ROOT / "neural" / "training-data" / "finetune_data.jsonl"

# Конфигурация
VARIATIONS_PER_TERM = 3
VARIATIONS_PER_RESEARCH = 2


def clean_text(text: str, max_length: int = 2000) -> str:
    """Очищает текст от метаданных и лишних символов"""
    # Убираем блок метаданных
    text = re.sub(r'\*\*Метаданные файла\*\*.*?\n---\n', '', text, flags=re.DOTALL)
    # Убираем эмодзи в начале строк
    text = re.sub(r'^# [\U00010000-\U0010FFFF]', '# ', text, flags=re.MULTILINE)
    # Ограничиваем длину
    return text[:max_length].strip()


def load_terminology() -> list:
    """Загружает термины и генерирует пары вопрос-ответ"""
    data = []
    question_templates = [
        "Что такое {name} в ТаНаХе?",
        "Объясни понятие {name}",
        "Что означает слово {name} на иврите?",
        "Расскажи о термине {name}",
        "Дай определение {name}",
        "Как переводится {name}?",
    ]

    for md_file in TERMINOLOGY_DIR.glob("*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Извлекаем заголовок (эмоджи + КАПС)
        title_match = re.search(r'^# .*?([А-ЯЁ\s]+)$', content, re.MULTILINE)
        if title_match:
            name_ru = title_match.group(1).strip().lower()
        else:
            name_ru = md_file.stem.replace('-', ' ')

        answer = clean_text(content, 1500)
        if not answer:
            continue

        # Генерируем несколько вариантов вопроса для каждого термина
        templates = random.sample(question_templates, min(VARIATIONS_PER_TERM, len(question_templates)))
        for template in templates:
            question = template.format(name=name_ru)
            data.append({
                "instruction": question,
                "output": answer,
                "source": md_file.name
            })

    return data


def load_researches() -> list:
    """Загружает исследования и генерирует пары вопрос-ответ"""
    data = []
    question_templates = [
        "Расскажи об исследовании {title}",
        "Что говорится в работе {title}?",
        "Краткое содержание: {title}",
        "Основные выводы исследования {title}",
        "О чём исследование {title}?",
    ]

    for md_file in RESEARCHES_DIR.rglob("*.md"):
        if md_file.name in ['README.md', 'STRUCTURE.md']:
            continue

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Извлекаем заголовок
        title_match = re.search(r'^# .*?([А-ЯЁ\s\(\)\-]+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            title = md_file.stem.replace('-', ' ')

        # Извлекаем введение или первый параграф
        intro_match = re.search(r'## 🔥 ВВЕДЕНИЕ\n\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if intro_match:
            answer = clean_text(intro_match.group(1), 1500)
        else:
            answer = clean_text(content[:1500], 1500)

        if not answer:
            continue

        templates = random.sample(question_templates, min(VARIATIONS_PER_RESEARCH, len(question_templates)))
        for template in templates:
            question = template.format(title=title)
            data.append({
                "instruction": question,
                "output": answer,
                "source": md_file.name
            })

    return data


def load_verses() -> list:
    """Генерирует вопросы о стихах ТаНаХа (из существующих файлов)"""
    data = []

    # Ищем стихи в файлах исследований и терминов
    verse_pattern = r'([\u0590-\u05FFa-zA-Zа-яА-Я]+)\s+(\d+):(\d+)'

    for md_file in list(TERMINOLOGY_DIR.glob("*.md")) + list(RESEARCHES_DIR.glob("*.md")):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = re.findall(verse_pattern, content)
        for book, chapter, verse in matches[:5]:  # не больше 5 на файл
            # Ищем перевод стиха в том же файле
            context = re.search(rf'{book}\s+{chapter}:{verse}.*?\n\n(.*?)(?=\n\n|\Z)', content, re.DOTALL)
            if context:
                verse_text = clean_text(context.group(1), 500)
                question = f"Переведи или объясни стих {book} {chapter}:{verse}"
                data.append({
                    "instruction": question,
                    "output": verse_text,
                    "source": md_file.name
                })

    return data


def generate_variations(data: list) -> list:
    """Генерирует дополнительные вариации уже существующих данных"""
    new_data = []

    paraphrases = [
        ("что такое", "что значит"),
        ("объясни", "расскажи о"),
        ("определение", "значение"),
        ("в ТаНаХе", "по ТаНаХу"),
        ("на иврите", "в оригинале"),
    ]

    for item in data[:]:  # работаем с копией
        for _ in range(1):  # одна вариация на каждый исходный
            new_instruction = item["instruction"]
            for old, new in paraphrases:
                if old in new_instruction.lower():
                    new_instruction = new_instruction.lower().replace(old, new)
                    break

            if new_instruction != item["instruction"]:
                new_data.append({
                    "instruction": new_instruction.capitalize(),
                    "output": item["output"],
                    "source": f"variation_of_{item['source']}"
                })

    return new_data


def main():
    print("📊 ПОДГОТОВКА ДАННЫХ ДЛЯ FINE-TUNE")
    print("=" * 50)

    all_data = []

    print("1. Загрузка терминов...")
    terms = load_terminology()
    print(f"   Добавлено: {len(terms)}")
    all_data.extend(terms)

    print("2. Загрузка исследований...")
    researches = load_researches()
    print(f"   Добавлено: {len(researches)}")
    all_data.extend(researches)

    print("3. Загрузка стихов...")
    verses = load_verses()
    print(f"   Добавлено: {len(verses)}")
    all_data.extend(verses)

    print("4. Генерация вариаций...")
    variations = generate_variations(all_data)
    print(f"   Добавлено: {len(variations)}")
    all_data.extend(variations)

    print("5. Перемешивание...")
    random.shuffle(all_data)

    # Сохраняем в JSONL
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for item in all_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print("=" * 50)
    print(f"✅ Всего записей: {len(all_data)}")
    print(f"✅ Сохранено: {OUTPUT_FILE}")

    # Показываем пример
    print("\n📋 ПРИМЕР ЗАПИСИ:")
    print(json.dumps(all_data[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

