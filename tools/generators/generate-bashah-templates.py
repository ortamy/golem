# tools/generators/generate-bashah-templates.py — создаёт пустые .md шаблоны для раздела БаШаХ
"""
Генератор шаблонов для раздела БаШаХ проекта «Голем».
Читает шаблоны из instructions/templates/ и создаёт пустые заготовки
в соответствующих папках content/bashah/. Не перезаписывает существующие файлы.
"""

import os
from datetime import date

TODAY = date.today().isoformat()
PROJECT_ROOT = "."

TEMPLATE_TO_FOLDER = {
    "TEMPLATE-TERM": "content/bashah/terminology",
    "TEMPLATE-TEACHING": "content/bashah/teachings",
    "TEMPLATE-BOOK": "content/bashah/books",
    "TEMPLATE-PERSON": "content/bashah/persons",
    "TEMPLATE-EVENT": "content/bashah/events",
    "TEMPLATE-PRACTICE": "content/bashah/practices",
}

MANUAL_TEMPLATES = {
    "concept": "content/bashah/concepts",
    "chronology": "content/bashah/chronology",
    "manuscript": "content/bashah/manuscripts",
    "geography": "content/bashah/geography",
    "nevua": "content/bashah/nevua",
    "letter": "content/bashah/letters",
}


def make_metadata(file_path):
    return f"""**Метаданные файла**
- **Файл:** `{file_path}`
- **Версия:** 1.0
- **Дата создания:** {TODAY}
- **Последнее обновление:** {TODAY}
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:**
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:**
- **Хеш:** ожидает
- **Достоверность:** низкая
- **Последний аудит:** {TODAY}
- **Уровень:** 🟡 Средний
"""


def load_template(template_name):
    template_path = os.path.join(
        PROJECT_ROOT, "instructions", "templates", f"{template_name}.md"
    )
    if not os.path.exists(template_path):
        return None
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("---", 2)
    if len(parts) >= 3:
        return "---" + parts[2]
    for i, line in enumerate(content.split("\n")):
        if line.startswith("## "):
            return "\n".join(content.split("\n")[i:])
    return content


def create_file(file_path, template_name=None):
    dir_path = os.path.dirname(file_path)
    full_dir = os.path.join(PROJECT_ROOT, dir_path)
    os.makedirs(full_dir, exist_ok=True)

    full_path = os.path.join(PROJECT_ROOT, file_path)
    if os.path.exists(full_path):
        print(f"  ⏭ {file_path}")
        return

    content = None
    if template_name:
        template_body = load_template(template_name)
        if template_body:
            content = f"---\n{make_metadata(file_path)}\n---\n{template_body}"

    if content is None:
        content = f"---\n{make_metadata(file_path)}\n---\n\n"

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ {file_path}")


def main():
    print("=" * 60)
    print("Генератор шаблонов БаШаХ — проект «Голем»")
    print("=" * 60)

    print("\n📋 Книги (TEMPLATE-BOOK)")
    print("-" * 40)
    for p in [
        "content/bashah/books/besorah-mattityahu.md",
        "content/bashah/books/besorah-markus.md",
        "content/bashah/books/besorah-luka.md",
        "content/bashah/books/besorah-yohanan.md",
        "content/bashah/books/maasei-shlichim.md",
        "content/bashah/books/hitgalut.md",
    ]:
        create_file(p, "TEMPLATE-BOOK")

    print("\n📋 Послания (letter)")
    print("-" * 40)
    for p in [
        "content/bashah/letters/romans.md",
        "content/bashah/letters/corinthians-alef.md",
        "content/bashah/letters/corinthians-bet.md",
        "content/bashah/letters/galatians.md",
        "content/bashah/letters/ephesians.md",
        "content/bashah/letters/philippians.md",
        "content/bashah/letters/colossians.md",
        "content/bashah/letters/thessalonians-alef.md",
        "content/bashah/letters/thessalonians-bet.md",
        "content/bashah/letters/timothy-alef.md",
        "content/bashah/letters/timothy-bet.md",
        "content/bashah/letters/titus.md",
        "content/bashah/letters/philemon.md",
        "content/bashah/letters/ivrim.md",
        "content/bashah/letters/yaakov.md",
        "content/bashah/letters/keifa-alef.md",
        "content/bashah/letters/keifa-bet.md",
        "content/bashah/letters/yohanan-alef.md",
        "content/bashah/letters/yohanan-bet.md",
        "content/bashah/letters/yohanan-gimel.md",
        "content/bashah/letters/yehudah.md",
    ]:
        create_file(p, "letter")

    print("\n📋 Личности (TEMPLATE-PERSON)")
    print("-" * 40)
    for p in [
        "content/bashah/persons/yohanan-matbil.md",
        "content/bashah/persons/keifa.md",
        "content/bashah/persons/yaakov-achim.md",
        "content/bashah/persons/yohanan-talmid.md",
        "content/bashah/persons/shaul.md",
        "content/bashah/persons/luka.md",
        "content/bashah/persons/mattityahu.md",
        "content/bashah/persons/markus.md",
        "content/bashah/persons/yaakov-shlichim.md",
        "content/bashah/persons/yehudah.md",
        "content/bashah/persons/miryam-magdalit.md",
        "content/bashah/persons/marta.md",
        "content/bashah/persons/elyakim.md",
        "content/bashah/persons/chananyah.md",
        "content/bashah/persons/shoshannah.md",
        "content/bashah/persons/yochanan-kohen.md",
        "content/bashah/persons/bar-abba.md",
        "content/bashah/persons/nakdimon.md",
        "content/bashah/persons/shimon-kfar-nachum.md",
        "content/bashah/persons/natanael.md",
        "content/bashah/persons/andrey.md",
        "content/bashah/persons/philipus.md",
        "content/bashah/persons/toma.md",
        "content/bashah/persons/mattityahu-levi.md",
    ]:
        create_file(p, "TEMPLATE-PERSON")

    print("\n📋 События (TEMPLATE-EVENT)")
    print("-" * 40)
    for p in [
        "content/bashah/events/tvilat-yeshua.md",
        "content/bashah/events/seudat-aharon.md",
        "content/bashah/events/shavuot-ruach.md",
        "content/bashah/events/petach-kefas.md",
        "content/bashah/events/beit-chananyah.md",
    ]:
        create_file(p, "TEMPLATE-EVENT")

    print("\n📋 Учения (TEMPLATE-TEACHING)")
    print("-" * 40)
    for p in [
        "content/bashah/teachings/drashat-hahar.md",
        "content/bashah/teachings/mashal-zorea.md",
        "content/bashah/teachings/tfilat-yeshua-teaching.md",
        "content/bashah/teachings/mashal-ben-sorer.md",
        "content/bashah/teachings/mashal-shomer-tzon.md",
    ]:
        create_file(p, "TEMPLATE-TEACHING")

    print("\n📋 Термины (TEMPLATE-TERM)")
    print("-" * 40)
    for p in [
        "content/bashah/terminology/bsora.md",
        "content/bashah/terminology/kehillah.md",
        "content/bashah/terminology/shaliah.md",
        "content/bashah/terminology/tvilah.md",
        "content/bashah/terminology/shutafut.md",
        "content/bashah/terminology/pesha.md",
    ]:
        create_file(p, "TEMPLATE-TERM")

    print("\n📋 Концепты (concept)")
    print("-" * 40)
    for p in [
        "content/bashah/concepts/besorah-concept.md",
        "content/bashah/concepts/kehillah-concept.md",
        "content/bashah/concepts/brit-hadashah.md",
        "content/bashah/concepts/psychikos-pneumatikos.md",
        "content/bashah/concepts/mashiah-bashah.md",
    ]:
        create_file(p, "concept")

    print("\n📋 Практики (TEMPLATE-PRACTICE)")
    print("-" * 40)
    for p in [
        "content/bashah/practices/tvilat-ruach.md",
        "content/bashah/practices/seuda-adon.md",
        "content/bashah/practices/smicha.md",
        "content/bashah/practices/tfilat-kehillah.md",
    ]:
        create_file(p, "TEMPLATE-PRACTICE")

    print("\n📋 Хронология (chronology)")
    print("-" * 40)
    create_file("content/bashah/chronology/timeline.md", "chronology")

    print("\n📋 Рукописи (manuscript)")
    print("-" * 40)
    for p in [
        "content/bashah/manuscripts/peshitta.md",
        "content/bashah/manuscripts/greek-manuscripts.md",
    ]:
        create_file(p, "manuscript")

    print("\n📋 География (geography)")
    print("-" * 40)
    for p in [
        "content/bashah/geography/yerushalaim.md",
        "content/bashah/geography/nazeret.md",
        "content/bashah/geography/kfar-nachum.md",
        "content/bashah/geography/antiohia.md",
        "content/bashah/geography/corinth.md",
        "content/bashah/geography/ephesus.md",
        "content/bashah/geography/roma.md",
    ]:
        create_file(p, "geography")

    print("\n📋 Невуа (nevua)")
    print("-" * 40)
    for p in [
        "content/bashah/nevua/hurban-bayit.md",
        "content/bashah/nevua/hitgalut-yohanan.md",
    ]:
        create_file(p, "nevua")

    print("\n" + "=" * 60)
    print("Генерация шаблонов БаШаХ завершена.")
    print("=" * 60)


if __name__ == "__main__":
    main()