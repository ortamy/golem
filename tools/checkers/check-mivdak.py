#!/usr/bin/env python3
# tools/checkers/check-mivdak.py — аудит полезности текстов (v1.0)

import sys
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent
CONTENT = ROOT / "content"

REQUIRED_SECTIONS = {
    "terminology": [
        "СУТЬ", "ЭТИМОЛОГИЯ", "ПАЛЕО-ИВРИТ", "КОНТЕКСТ ТАНАХА",
        "ТРАНСФОРМАЦИЯ", "РАЗОБЛАЧЕНИЕ", "СВОДКА"
    ],
    "research": [
        "ВВЕДЕНИЕ", "ЭТИМОЛОГИЯ", "КОНТЕКСТ ТАНАХА",
        "ТРАНСФОРМАЦИЯ", "РАЗОБЛАЧЕНИЕ", "СВОДКА"
    ],
    "teaching": [
        "ЧТО ЭТО", "СЕМЯ", "ПОЧВА", "КОРНИ",
        "СТВОЛ", "ВЕТВИ", "ПЛОДЫ", "РАЗОБЛАЧЕНИЕ", "СВОДКА"
    ],
    "exposure": [
        "ЧТО ЭТО", "АРХИТЕКТУРА СИСТЕМЫ", "ЧТО ГОВОРИТ ТАНАХ",
        "РАЗОБЛАЧЕНИЕ", "СВОДКА"
    ],
    "book": [
        "ОБЩИЕ СВЕДЕНИЯ", "СТРУКТУРА КНИГИ", "КЛЮЧЕВЫЕ ТЕМЫ",
        "СВЯЗЬ С МАШИАХОМ", "СВОДКА"
    ],
    "person": [
        "ОБЩИЕ СВЕДЕНИЯ", "ЖИЗНЕОПИСАНИЕ", "ОШИБКИ И ПАДЕНИЯ",
        "СВЯЗЬ С МАШИАХОМ", "СВОДКА"
    ],
    "event": [
        "ОБЩИЕ СВЕДЕНИЯ", "ПРЕДЫСТОРИЯ", "ХОД СОБЫТИЯ",
        "СВЯЗЬ С МАШИАХОМ", "СВОДКА"
    ],
    "practice": [
        "ЧТО ЭТО", "ПРАКТИКА В ТАНАХЕ", "КАК ИСКАЗИЛОСЬ",
        "КАК ВОСТАНОВИТЬ", "СВОДКА"
    ],
    "learn": [
        "О ЧЁМ ЭТОТ УРОК", "ТЕОРИЯ", "ПРАВИЛО",
        "ПРИМЕРЫ ИЗ ТАНАХА", "УПРАЖНЕНИЯ", "СВОДКА"
    ],
}

EXPOSURE_METHODS = [
    "этимологический удар", "сравнение переводов", "конкретизация",
    "корневые связи", "обратный перевод", "транслитерация",
    "семитский синтаксис", "исторический контекст", "плоды",
    "сад", "труба", "древнее письмо", "возвращение образов",
    "распознавание муштры", "узкие места", "две системы",
    "язык творения", "карта сдвига", "пустыня", "змей",
    "ваалам", "колизей", "помазание", "этимологическое разоблачение",
    "юридическая археология", "архитектурное разоблачение",
    "исторический слой", "проверка символа", "финансовое разоблачение",
    "этимологическое возвращение", "глагольное возвращение", "вскрытие пустого слова"
]

DISTORTION_TYPES = [
    "подмена категории", "юридизация", "психологизация",
    "сдвиг от действия к эмоции", "абстракция", "сужение смысла",
    "дуализация", "кастрация смысла"
]


def detect_type(filepath):
    """Определяет тип файла по пути."""
    rel = str(filepath.relative_to(CONTENT))
    parts = rel.split("/")
    
    if parts[0] == "terminology":
        return "terminology"
    if parts[0] == "teachings":
        return "teaching"
    if parts[0] == "learn-hebrew":
        return "learn"
    if parts[0] == "practices":
        return "practice"
    if parts[0] == "tanakh":
        if len(parts) > 2:
            if parts[1] == "books": return "book"
            if parts[1] == "persons": return "person"
            if parts[1] == "events": return "event"
        return "research"
    if parts[0] == "bashah":
        return "research"
    if parts[0] == "researches":
        return "research"
    
    return "research"


def check_file(filepath):
    """Проверяет один файл на соответствие шаблону."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"error": "не читается"}
    
    file_type = detect_type(filepath)
    required = REQUIRED_SECTIONS.get(file_type, REQUIRED_SECTIONS["research"])
    
    result = {
        "path": str(filepath.relative_to(ROOT)).replace("\\", "/"),
        "type": file_type,
        "has_metadata": "**Метаданные файла**" in content,
        "has_related": "**Связанные файлы:**" in content,
        "has_hebrew": bool(re.search(r'[\u0590-\u05FF]{2,}', content)),
        "has_transliteration": bool(re.search(r'\*[a-zа-яё]+\*', content)),
        "has_verses": len(re.findall(r'\d+:\d+', content)) >= 1,
        "sections_found": [],
        "sections_missing": [],
        "methods_found": [],
        "distortions_found": [],
        "score": 0,
    }
    
    # Проверяем разделы
    for section in required:
        pattern = re.compile(r'^##\s+[^\n]*' + re.escape(section) + r'[^\n]*$', re.MULTILINE | re.IGNORECASE)
        if pattern.search(content):
            result["sections_found"].append(section)
        else:
            result["sections_missing"].append(section)
    
    # Ищем методы exposure
    for method in EXPOSURE_METHODS:
        if method.lower() in content.lower():
            result["methods_found"].append(method)
    
    # Ищем типы искажений
    for dtype in DISTORTION_TYPES:
        if dtype.lower() in content.lower():
            result["distortions_found"].append(dtype)
    
    # Считаем баллы
    score = 0
    if result["has_metadata"]: score += 10
    if result["has_related"]: score += 5
    if result["has_hebrew"]: score += 10
    if result["has_verses"]: score += 10
    score += len(result["sections_found"]) * 5
    score += len(result["methods_found"]) * 2
    score += len(result["distortions_found"]) * 2
    score -= len(result["sections_missing"]) * 5
    
    result["score"] = max(0, score)
    
    if score >= 50: result["verdict"] = "✅ Качественный"
    elif score >= 30: result["verdict"] = "👍 Хороший"
    elif score >= 15: result["verdict"] = "⚠️ Требует доработки"
    else: result["verdict"] = "❌ Пустой"
    
    return result


def main():
    print("🔍 Аудит полезности текстов (mivdak)...\n")
    
    results = []
    stats = defaultdict(lambda: {"total": 0, "good": 0, "bad": 0})
    
    all_files = sorted(CONTENT.rglob("*.md"))
    total = len(all_files)
    
    for i, md_file in enumerate(all_files, 1):
        if md_file.name in ["README.md", "STRUCTURE.md", "GLOSSARY.md", "CHANGELOG.md"]:
            continue
        
        result = check_file(md_file)
        results.append(result)
        
        file_type = result["type"]
        stats[file_type]["total"] += 1
        if result["verdict"].startswith("✅") or result["verdict"].startswith("👍"):
            stats[file_type]["good"] += 1
        else:
            stats[file_type]["bad"] += 1
        
        if i % 100 == 0:
            print(f"  Проверено: {i}/{total}...")
    
    # Статистика по типам
    print(f"\n📊 Качество по типам файлов:")
    for ftype in sorted(stats.keys()):
        s = stats[ftype]
        pct = round(s["good"] / s["total"] * 100) if s["total"] > 0 else 0
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
        print(f"  {ftype:15} {bar} {pct:3}% ({s['good']}/{s['total']})")
    
    # Общая статистика
    good = [r for r in results if r["verdict"].startswith("✅") or r["verdict"].startswith("👍")]
    bad = [r for r in results if not (r["verdict"].startswith("✅") or r["verdict"].startswith("👍"))]
    
    print(f"\n📝 Всего файлов: {len(results)}")
    print(f"   ✅ Качественных: {len(good)}")
    print(f"   ❌ Требуют доработки: {len(bad)}")
    
    # Топ проблемных
    if bad:
        print(f"\n⚠️ Худшие 10 файлов:")
        worst = sorted(bad, key=lambda r: r["score"])[:10]
        for r in worst:
            missing = ", ".join(r["sections_missing"][:3])
            if len(r["sections_missing"]) > 3:
                missing += f" +{len(r['sections_missing']) - 3}"
            print(f"  {r['score']:3} баллов  {r['path']}")
            if r["sections_missing"]:
                print(f"         Нет разделов: {missing}")
    
    # Топ лучших
    if good:
        print(f"\n🌟 Лучшие 5 файлов:")
        best = sorted(good, key=lambda r: r["score"], reverse=True)[:5]
        for r in best:
            print(f"  {r['score']:3} баллов  {r['path']}")
            print(f"         Разделов: {len(r['sections_found'])}, методов: {len(r['methods_found'])}, искажений: {len(r['distortions_found'])}")


if __name__ == "__main__":
    main()