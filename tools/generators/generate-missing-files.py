#!/usr/bin/env python3
# tools/generators/generate-missing-files.py — создаёт отсутствующие файлы по шаблонам

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = ROOT / "instructions" / "templates"
METADATA_FILE = ROOT / "tools" / "cache" / "cache-metadata-templates.json"
CONTENT = ROOT / "content"

# Соответствие типа файла → шаблон .md
TYPE_TO_TEMPLATE = {
    "terminology": "TEMPLATE-TERM.md",
    "research": "TEMPLATE-RESEARCH.md",
    "teaching": "TEMPLATE-TEACHING.md",
    "exposure": "TEMPLATE-EXPOSURE.md",
    "book": "TEMPLATE-BOOK.md",
    "person": "TEMPLATE-PERSON.md",
    "event": "TEMPLATE-EVENT.md",
    "practice": "TEMPLATE-PRACTICE.md",
    "learn": "TEMPLATE-LEARN.md",
}

# Ожидаемые файлы по категориям (можно дополнять)
EXPECTED_FILES = {
    "terminology": [],  # все что есть в папке — уже правильно
    "research": [],     # все что есть — правильно
    "teaching": [],     # уже сгенерированы 254 файла
    "book": [
        "content/tanakh/books/bereshit.md",
        "content/tanakh/books/shmot.md",
        "content/tanakh/books/vayikra.md",
        "content/tanakh/books/bemidbar.md",
        "content/tanakh/books/dvarim.md",
        "content/tanakh/books/yehoshua.md",
        "content/tanakh/books/shoftim.md",
        "content/tanakh/books/shmuel-alef.md",
        "content/tanakh/books/shmuel-bet.md",
        "content/tanakh/books/melachim-alef.md",
        "content/tanakh/books/melachim-bet.md",
        "content/tanakh/books/yeshayahu.md",
        "content/tanakh/books/yirmeyahu.md",
        "content/tanakh/books/yehezkel.md",
        "content/tanakh/books/hoshea.md",
        "content/tanakh/books/yoel.md",
        "content/tanakh/books/amos.md",
        "content/tanakh/books/ovadyah.md",
        "content/tanakh/books/yonah.md",
        "content/tanakh/books/mikhah.md",
        "content/tanakh/books/nachum.md",
        "content/tanakh/books/chavakuk.md",
        "content/tanakh/books/tsefanyah.md",
        "content/tanakh/books/chaggai.md",
        "content/tanakh/books/zechariah.md",
        "content/tanakh/books/malakhi.md",
        "content/tanakh/books/tehillim.md",
        "content/tanakh/books/mishlei.md",
        "content/tanakh/books/iyov.md",
        "content/tanakh/books/shir-hashirim.md",
        "content/tanakh/books/rut.md",
        "content/tanakh/books/eikhah.md",
        "content/tanakh/books/kohelet.md",
        "content/tanakh/books/ester.md",
        "content/tanakh/books/daniel.md",
        "content/tanakh/books/ezra.md",
        "content/tanakh/books/nechemyah.md",
        "content/tanakh/books/divrei-hayamim-alef.md",
        "content/tanakh/books/divrei-hayamim-bet.md",
    ],
    "person": [
        "content/tanakh/persons/avraham.md",
        "content/tanakh/persons/itzchak.md",
        "content/tanakh/persons/yaakov.md",
        "content/tanakh/persons/yosef.md",
        "content/tanakh/persons/moshe.md",
        "content/tanakh/persons/aharon.md",
        "content/tanakh/persons/yehoshua.md",
        "content/tanakh/persons/dvorah.md",
        "content/tanakh/persons/gidon.md",
        "content/tanakh/persons/shimshon.md",
        "content/tanakh/persons/rut-person.md",
        "content/tanakh/persons/shmuel.md",
        "content/tanakh/persons/shaul.md",
        "content/tanakh/persons/david.md",
        "content/tanakh/persons/shlomo.md",
        "content/tanakh/persons/eliyahu.md",
        "content/tanakh/persons/elisha.md",
        "content/tanakh/persons/yeshayahu-person.md",
        "content/tanakh/persons/yirmeyahu-person.md",
        "content/tanakh/persons/yehezkel-person.md",
        "content/tanakh/persons/daniel-person.md",
        "content/tanakh/persons/ester-person.md",
        "content/tanakh/persons/ezra-person.md",
        "content/tanakh/persons/nechemyah-person.md",
    ],
    "event": [
        "content/tanakh/events/briat-haolam.md",
        "content/tanakh/events/mabul.md",
        "content/tanakh/events/brit-bein-habetarim.md",
        "content/tanakh/events/akedat-itzchak.md",
        "content/tanakh/events/yetziat-mitzraim.md",
        "content/tanakh/events/kriat-yam-suf.md",
        "content/tanakh/events/matan-torah.md",
        "content/tanakh/events/chet-haegel.md",
        "content/tanakh/events/meraglim.md",
        "content/tanakh/events/mey-merivah.md",
        "content/tanakh/events/nechash-nechoshet.md",
        "content/tanakh/events/brit-moav.md",
        "content/tanakh/events/petach-hayarden.md",
        "content/tanakh/events/kriat-yericho.md",
        "content/tanakh/events/chet-achan.md",
        "content/tanakh/events/milchemet-ai.md",
        "content/tanakh/events/brit-begivon.md",
        "content/tanakh/events/milchemet-dvorah.md",
        "content/tanakh/events/milchemet-gidon.md",
        "content/tanakh/events/nefilat-shimshon.md",
        "content/tanakh/events/pesel-michah.md",
        "content/tanakh/events/pilegesh-bagivah.md",
        "content/tanakh/events/mashiach-david.md",
        "content/tanakh/events/chet-david.md",
        "content/tanakh/events/mered-avshalom.md",
        "content/tanakh/events/binyan-habayit.md",
        "content/tanakh/events/churban-bayit-rishon.md",
        "content/tanakh/events/galut-bavel.md",
        "content/tanakh/events/shivat-tzion.md",
        "content/tanakh/events/binyan-bayit-sheni.md",
        "content/tanakh/events/purim.md",
        "content/tanakh/events/chanukah.md",
    ],
    "practice": [
        "content/practices/shabbat.md",
        "content/practices/tvilah.md",
        "content/practices/tfilah.md",
        "content/practices/tsom.md",
        "content/practices/tsedakah.md",
        "content/practices/brit-milah.md",
        "content/practices/kashrut.md",
        "content/practices/aliyah-laregel.md",
        "content/practices/shemittah.md",
        "content/practices/yovel.md",
        "content/practices/korban-pesach.md",
        "content/practices/shavuot-practice.md",
        "content/practices/sukkot.md",
        "content/practices/yom-truah.md",
        "content/practices/yom-kippur.md",
    ],
    "learn": [],  # уже есть 5 файлов
}


def generate():
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata_config = json.load(f)
    
    templates_cache = {}
    created = 0
    skipped = 0
    errors = 0
    
    for file_type, expected_paths in EXPECTED_FILES.items():
        if not expected_paths:
            continue
        
        # Загружаем шаблон
        template_name = TYPE_TO_TEMPLATE.get(file_type)
        if not template_name:
            continue
        
        template_path = TEMPLATES_DIR / template_name
        if template_path not in templates_cache:
            if template_path.exists():
                templates_cache[template_path] = template_path.read_text(encoding="utf-8")
            else:
                print(f"⚠️ Шаблон не найден: {template_name}")
                continue
        
        template_content = templates_cache[template_path]
        
        # Получаем конфиг метаданных для этого типа
        meta_config = metadata_config.get("templates", {}).get(file_type)
        if not meta_config:
            continue
        
        for file_path_str in expected_paths:
            file_path = ROOT / file_path_str
            
            if file_path.exists():
                skipped += 1
                continue
            
            # Создаём папку если нужно
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Формируем метаданные
            filename = file_path.stem
            metadata_block = _build_metadata(meta_config, filename, file_path_str)
            
            # Собираем файл: метаданные + шаблон
            full_content = metadata_block + "\n---\n\n" + template_content
            
            file_path.write_text(full_content, encoding="utf-8")
            created += 1
            print(f"✅ {file_path_str}")
    
    print(f"\n✅ Создано: {created}")
    print(f"⏭️ Пропущено (уже есть): {skipped}")
    print(f"❌ Ошибок: {errors}")


def _build_metadata(meta_config, filename, file_path_str):
    """Строит блок метаданных из конфига."""
    fields = meta_config.get("fields", {})
    date = "2026-06-12"
    
    lines = ["**Метаданные файла**"]
    for field_name, field_value in fields.items():
        # Подстановка переменных
        field_value = field_value.replace("{filename}", filename)
        field_value = field_value.replace("{date}", date)
        lines.append(f"- **{field_name}:** {field_value}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    generate()