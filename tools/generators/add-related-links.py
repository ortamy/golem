# tools/generators/add-related-links.py — добавление блока «СВЯЗАННЫЕ ИССЛЕДОВАНИЯ»
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_hint, ask_yes_no, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions"]

# Ключевые слова → связанные файлы
KEYWORD_LINKS = {
    # exposure/
    "искажение": ["instructions/exposure/exposure-distortions.md"],
    "подмена": ["instructions/exposure/exposure-mechanisms.md", "instructions/exposure/exposure-techniques.md"],
    "механизм": ["instructions/exposure/exposure-mechanisms.md"],
    "приём": ["instructions/exposure/exposure-techniques.md"],
    "метод": ["instructions/exposure/exposure-methods.md"],
    "разоблачение": ["instructions/exposure/exposure-methods.md"],
    "религионизм": ["instructions/exposure/exposure-religionism-theory.md"],
    "система": ["instructions/exposure/exposure-system-architecture.md"],
    "язык": ["instructions/exposure/exposure-language-control.md"],
    "лингвист": ["instructions/exposure/exposure-language-control.md"],
    "контроль": ["instructions/exposure/exposure-system-architecture.md"],
    "архитектура": ["instructions/exposure/exposure-system-architecture.md"],
    "принцип": ["instructions/exposure/exposure-principles.md"],

    # tahor/
    "грецизм": ["instructions/tahor/grecisms.md"],
    "латинизм": ["instructions/tahor/latinisms.md"],
    "славянизм": ["instructions/tahor/slavicisms.md"],
    "религионим": ["instructions/tahor/religionisms.md"],
    "имя": ["instructions/tahor/names.md"],
    "фраза": ["instructions/tahor/phrases.md"],

    # methodology/
    "перевод": ["instructions/methodology/translation-methodology.md"],
    "транслитерация": ["instructions/methodology/transliteration-distortions.md"],
    "археология": ["instructions/methodology/archeology-methodology.md"],
    "иврит": ["instructions/methodology/hebrew-reconstruction.md"],
    "дерево": ["instructions/methodology/tree-method.md"],
    "учение": ["instructions/methodology/tree-method.md"],

    # economy/
    "банк": ["researches/economy/history-of-banks.md", "researches/economy/banks-and-financial-dynasties.md"],
    "деньги": ["researches/economy/history-of-money.md"],
    "экономик": ["researches/economy/history-of-economy.md"],
    "ипотека": ["researches/economy/mortgage-dead-pledge.md"],
    "кредит": ["researches/economy/mortgage-dead-pledge.md", "researches/economy/banks-and-financial-dynasties.md"],
    "долг": ["researches/economy/mortgage-dead-pledge.md", "researches/economy/banks-and-financial-dynasties.md", "researches/economy/economic-slavery.md"],
    "шмита": ["terminology/shmitah.md", "terminology/yovel.md"],
    "йовель": ["terminology/yovel.md", "terminology/shmitah.md"],
    "процент": ["researches/economy/mortgage-dead-pledge.md"],
    "ростовщи": ["researches/economy/mortgage-dead-pledge.md"],
    "рабств": ["researches/economy/economic-slavery.md", "researches/slavery/economic-slavery.md"],
    "финанс": ["researches/economy/banks-and-financial-dynasties.md", "researches/economy/history-of-banks.md"],

    # history/
    "алхимия": ["researches/history/alchemy.md"],
    "алхимик": ["researches/history/alchemy.md"],
    "парацельс": ["researches/other/paracelsus.md"],
    "никей": ["researches/history/nicaea-council.md"],
    "собор": ["researches/history/nicaea-council.md"],

    # tanakh/
    "маген": ["researches/tanakh/magen-david.md"],
    "давид": ["researches/tanakh/magen-david.md"],
    "звезда": ["researches/tanakh/magen-david.md"],
    "гог": ["researches/tanakh/gog-and-magog.md"],
    "магог": ["researches/tanakh/gog-and-magog.md"],
    "шаббат": ["terminology/shabbat.md"],
    "тора": ["terminology/torah.md"],
    "яхве": ["terminology/yhwh.md"],
    "yhwh": ["terminology/yhwh.md"],
    "элоhим": ["terminology/el.md"],
    "машиах": ["terminology/mashiah-peshat.md"],
}

# Файлы, которые НЕ нужно трогать
SKIP_FILES = {
    "README.md", "STRUCTURE.md", "GLOSSARY.md", "STATS.md", "CHANGELOG.md",
    "BACKLOG.md", "DECISIONS.md", "ROADMAP.md", "TECHNICAL-DEBT.md", "RETROSPECTIVE.md",
    "CONTRIBUTORS.md", "COMPLETED-TASKS.md",
}

# Файлы, у которых уже есть блок «СВЯЗАННЫЕ ИССЛЕДОВАНИЯ»
ALREADY_HAS_LINKS = set()


def extract_existing_links(content: str) -> set:
    """Извлекает существующие ссылки из блока связанных исследований."""
    links = set()
    match = re.search(r'## 🔗 СВЯЗАННЫЕ ИССЛЕДОВАНИЯ\n(.*?)(?=\n---|\n# |\Z)', content, re.DOTALL)
    if match:
        for link in re.findall(r'`([^`]+)`', match.group(1)):
            links.add(link)
    return links


def find_relevant_links(content: str, filepath: str) -> list:
    """Находит релевантные ссылки на основе ключевых слов."""
    text_lower = content.lower()
    found_links = set()

    for keyword, links in KEYWORD_LINKS.items():
        if keyword in text_lower:
            for link in links:
                # Не ссылаемся на самого себя
                if link not in filepath:
                    found_links.add(link)

    # Убираем уже существующие ссылки
    existing = extract_existing_links(content)
    new_links = found_links - existing

    return sorted(new_links)


def add_links_block(content: str, new_links: list) -> str:
    """Добавляет или обновляет блок связанных исследований."""
    if not new_links:
        return content

    links_text = '\n'.join(f'- `{link}`' for link in new_links[:10])

    if '## 🔗 СВЯЗАННЫЕ ИССЛЕДОВАНИЯ' in content:
        # Дополняем существующий блок
        existing = extract_existing_links(content)
        all_links = sorted(existing | set(new_links))
        links_text = '\n'.join(f'- `{link}`' for link in all_links[:15])

        # Заменяем блок
        pattern = r'## 🔗 СВЯЗАННЫЕ ИССЛЕДОВАНИЯ\n.*?(?=\n---|\n# |\Z)'
        replacement = f'## 🔗 СВЯЗАННЫЕ ИССЛЕДОВАНИЯ\n{links_text}'
        return re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Добавляем новый блок перед последней цитатой или в конец
    block = f'\n\n---\n\n## 🔗 СВЯЗАННЫЕ ИССЛЕДОВАНИЯ\n{links_text}\n'

    # Ищем последнюю цитату (строку, начинающуюся с >)
    last_quote = re.search(r'(\n> .+)$', content, re.MULTILINE)
    if last_quote:
        pos = last_quote.start()
        return content[:pos] + block + content[pos:]

    return content + block


def main():
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    print_header("ДОБАВЛЕНИЕ СВЯЗАННЫХ ССЫЛОК" if not dry_run else "ПРЕДПРОСМОТР СВЯЗАННЫХ ССЫЛОК", "🔗")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            for md_file in dir_path.rglob("*.md"):
                if md_file.name not in SKIP_FILES:
                    all_files.append(md_file)

    total = len(all_files)
    print(f"Найдено файлов: {total}")

    updated = 0
    total_links_added = 0

    for i, filepath in enumerate(all_files, 1):
        content = read_file_safe(filepath)
        if not content:
            continue

        rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
        new_links = find_relevant_links(content, rel_path)

        if new_links:
            total_links_added += len(new_links)

            if not dry_run:
                new_content = add_links_block(content, new_links)
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    updated += 1

        progress_bar(i, total, extra=f"обновлено: {updated} | ссылок: {total_links_added}")

    finish_progress()

    if dry_run:
        print_success(f"Будет добавлено {total_links_added} ссылок в {updated} файлов")
        print_hint("Для применения: python tools/generators/add-related-links.py")
    else:
        print_success(f"Добавлено {total_links_added} ссылок в {updated} файлов")

    return 0


if __name__ == "__main__":
    sys.exit(main())