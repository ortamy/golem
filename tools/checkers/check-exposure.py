# tools/checkers/check-exposure.py — полная проверка текста по всем exposure-критериям
import sys
import re
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_error, print_hint, ask_yes_no, REPO_ROOT

SCAN_DIRS = ["terminology", "researches"]

# =============================================================================
# МАРКЕРЫ ИСКАЖЕНИЙ (из exposure-techniques.md)
# =============================================================================

# 1. Подмена категории (живое → институт)
CATEGORY_SUBSTITUTION = [
    (r'\bзакон\b', "Тора = наставление, не закон"),
    (r'\bцерковь\b', "קהילה = собрание, не организация"),
    (r'\bхрам\b', "מקדש = место отделённости, не здание"),
    (r'\bсвященник\b', "כהן = служитель, не иерархический сан"),
    (r'\bзавет\b', "ברית = союз, не договор"),
]

# 2. Юридизация (союз → контракт)
JURIDIFICATION = [
    (r'\bгрех\b', "חטא = промах, не преступление"),
    (r'\bпокаяние\b', "תשובה = возвращение, не юридическое прощение"),
    (r'\bискупление\b', "כפרה = выкуп, не юридическая сделка"),
    (r'\bоправдание\b', "צדקה = справедливость, не вердикт"),
    (r'\bдолг\b', "долг ≠ грех; в иврите нет 'долга' перед Яхве"),
]

# 3. Психологизация (действие → чувство)
PSYCHOLOGIZATION = [
    (r'\bвера\b', "אמונה = верность в делах, не внутреннее чувство"),
    (r'\bпокаяние\b', "תשובה = физический разворот, не чувство вины"),
    (r'\bстрах Божий\b', "יראת יהוה = трепет-видение, не эмоция страха"),
    (r'\bсмирение\b', "ענווה = готовность учиться, не самоуничижение"),
    (r'\bлюбовь\b', "אהבה = действие, не только эмоция"),
]

# 4. Сдвиг от действия к эмоции
ACTION_TO_EMOTION = [
    (r'\bмилость\b', "חסד = преданная любовь в действии, не жалость"),
    (r'\bблагодать\b', "חן = благоволение, не абстрактная 'благодать'"),
    (r'\bмилосердие\b', "רחמים = действие милосердия, не чувство"),
    (r'\bсострадание\b', "רחמים = от רחם (матка), родственная забота в действии"),
]

# 5. Абстракция (конкретное → философское)
ABSTRACTION = [
    (r'\bдуша\b', "נפש = дышащее существо, не абстрактная субстанция"),
    (r'\bдух\b', "רוח = дыхание/ветер, не бесплотная сущность"),
    (r'\bистина\b', "אמת = надёжность, твёрдость, не абстрактная истина"),
    (r'\bслава\b', "כבוד = тяжесть/вес, не абстрактная 'слава'"),
    (r'\bсвятой\b', "קדוש = отделённый, не абстрактная 'святость'"),
    (r'\bспасение\b', "ישועה = избавление из беды, не абстрактное 'спасение души'"),
    (r'\bвечность\b', "עולם = скрытый горизонт, не бесконечность"),
    (r'\bад\b', "שאול = могила, не место вечных мук"),
    (r'\bрай\b', "גן עדן = сад Эден, не 'рай' как место блаженства"),
]

# 6. Сужение смысла (широкое → узкое)
MEANING_NARROWING = [
    (r'\bмилостыня\b', "צדקה = восстановление справедливости, не только подаяние"),
    (r'\bзакон\b', "תורה = всё наставление, не только запреты"),
    (r'\bпророк\b', "נביא = призванный вестник, не предсказатель"),
    (r'\bангел\b', "מלאך = вестник (может быть человеком), не крылатое существо"),
    (r'\bкрещение\b', "טבילה = погружение, не ритуал"),
    (r'\bевангелие\b', "בשורה = благая весть, не книга"),
    (r'\bапостол\b', "שליח = посланник, не титул"),
]

# 7. Дуализация (единое → противоположное)
DUALIZATION = [
    (r'\bветхий завет\b', "ТаНаХ — не 'ветхий', это живое слово"),
    (r'\bновый завет\b', "ברית חדשה = обновлённый союз, не 'новый' против 'старого'"),
    (r'\bзакон и благодать\b', "Тора и חן — не противоположности"),
    (r'\bдух и плоть\b', "רוח и בשר — оба от Яхве, не враги"),
    (r'\bдобро и зло\b', "טוב ורע = пригодное и разрушительное, не дуализм"),
    (r'\bсвет и тьма\b', "אור и חושך — не равные противоположности"),
]

# 8. Транслитерация вместо перевода (слова-обманки)
TRANSLITERATION_TRAPS = [
    (r'\bдьявол\b', "διάβολος = клеветник, не имя"),
    (r'\bсатана\b', "שטן = противник/обвинитель, не имя"),
    (r'\bепископ\b', "ἐπίσκοπος = надзиратель, не сан"),
    (r'\bдиакон\b', "διάκονος = служитель, не сан"),
    (r'\bлитургия\b', "λειτουργία = служение, не ритуал"),
    (r'\bевхаристия\b', "εὐχαριστία = благодарение, не таинство"),
    (r'\bпневма\b', "πνεῦμα = дыхание/ветер, не 'дух'"),
    (r'\bлогос\b', "λόγος = слово/дело (דבר), не философский 'Логос'"),
]

# 9. Имя подменено титулом
NAME_SUBSTITUTION = [
    (r'\bГосподь\b', "יהוה = Яхве, не 'Господь'"),
    (r'\bГосподи\b', "יהוה = Яхве, не 'Господи'"),
    (r'\bГоспода\b', "יהוה = Яхве, не 'Господа'"),
    (r'\bГосподом\b', "יהוה = Яхве, не 'Господом'"),
    (r'\bГосподе\b', "יהוה = Яхве, не 'Господе'"),
    (r'\bБог\b', "אלוהים или יהוה, не 'Бог'"),
    (r'\bБога\b', "אלוהים или יהוה, не 'Бога'"),
    (r'\bБогу\b', "אלוהים или יהוה, не 'Богу'"),
    (r'\bБогом\b', "אלוהים или יהוה, не 'Богом'"),
    (r'\bБоже\b', "אלוהים или יהוה, не 'Боже'"),
    (r'\bХристос\b', "משיח = Машиах (Помазанник), не 'Христос'"),
    (r'\bХриста\b', "משיח = Машиах, не 'Христа'"),
    (r'\bИисус\b', "יהושע = Йешуа, не 'Иисус'"),
    (r'\bИисуса\b', "יהושע = Йешуа, не 'Иисуса'"),
    (r'\bВсевышний\b', "עליון = Эльйон, или יהוה = Яхве"),
    (r'\bАдонай\b', "יהוה = Яхве; Адонай — традиционная замена"),
]

# 10. Мёртвый залог / финансовое рабство
FINANCIAL_SLAVERY = [
    (r'\bипотека\b', "mortgage = мёртвый залог; шмита = прощение долгов"),
    (r'\bкредит\b', "кредит ↔ шмита (прощение каждые 7 лет)"),
    (r'\bпроцент\b', "процент запрещён в Торе (Шмот 22:24)"),
    (r'\bдолг\b', "долг ↔ шмита; 'должник — раб заимодавца' (Мишлей 22:7)"),
    (r'\bпенсия\b', "пенсия ↔ йовель (возвращение земли каждые 50 лет)"),
]

ALL_MARKERS = {
    "Подмена категории (живое → институт)": CATEGORY_SUBSTITUTION,
    "Юридизация (союз → контракт)": JURIDIFICATION,
    "Психологизация (действие → чувство)": PSYCHOLOGIZATION,
    "Сдвиг от действия к эмоции": ACTION_TO_EMOTION,
    "Абстракция (конкретное → философское)": ABSTRACTION,
    "Сужение смысла (широкое → узкое)": MEANING_NARROWING,
    "Дуализация (единое → противоположное)": DUALIZATION,
    "Транслитерация вместо перевода": TRANSLITERATION_TRAPS,
    "Имя подменено титулом": NAME_SUBSTITUTION,
    "Финансовое рабство": FINANCIAL_SLAVERY,
}


def check_file(filepath: Path) -> dict:
    """Проверяет один файл по всем маркерам."""
    content = read_file_safe(filepath)
    if not content:
        return None

    # Защищаем метаданные и цитаты
    clean = content
    clean = re.sub(r'\*\*Метаданные файла\*\*.*?(?=\n---|\n# |\n## )', '', clean, flags=re.DOTALL)
    clean = re.sub(r'«[^»]*»|"[^"]*"|\'[^\']*\'', ' ', clean)

    findings = defaultdict(list)

    for category, markers in ALL_MARKERS.items():
        for pattern, explanation in markers:
            matches = re.finditer(pattern, clean, re.IGNORECASE)
            for match in matches:
                word = match.group()
                # Захватываем контекст (40 символов вокруг)
                start = max(0, match.start() - 40)
                end = min(len(clean), match.end() + 40)
                context = clean[start:end].replace('\n', ' ').strip()
                findings[category].append({
                    "word": word,
                    "context": f"...{context}...",
                    "fix": explanation
                })

    if findings:
        rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
        return {"path": rel_path, "findings": dict(findings)}

    return None


def main():
    print_header("ПОЛНАЯ ПРОВЕРКА ПО EXPOSURE", "🔍")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    print(f"Найдено файлов: {total}")
    print(f"Категорий проверки: {len(ALL_MARKERS)}")
    print(f"Маркеров: {sum(len(v) for v in ALL_MARKERS.values())}")

    results = []
    total_markers_found = 0
    category_stats = Counter()

    for i, filepath in enumerate(all_files, 1):
        result = check_file(filepath)
        if result:
            results.append(result)
            for category in result["findings"]:
                count = len(result["findings"][category])
                total_markers_found += count
                category_stats[category] += count

        progress_bar(i, total, extra=f"файлов: {len(results)} | маркеров: {total_markers_found}")

    finish_progress()

    if not results:
        print_success("Нарушений не найдено — текст чист по всем exposure-критериям")
        return 0

    print(f"\n📁 Файлов с нарушениями: {len(results)}")
    print(f"📝 Всего маркеров: {total_markers_found}\n")

    print("📊 По категориям:")
    for category, count in category_stats.most_common():
        bar = "█" * min(count, 40)
        print(f"  {category:40} {count:4}  {bar}")

    print(f"\n📋 Файлы с наибольшим числом нарушений (первые 10):")
    results.sort(key=lambda r: sum(len(v) for v in r["findings"].values()), reverse=True)
    for result in results[:10]:
        total = sum(len(v) for v in result["findings"].values())
        top_category = max(result["findings"], key=lambda k: len(result["findings"][k]))
        print(f"  • {result['path']} — {total} маркеров (чаще: {top_category})")

    print(f"\n🔍 Детали по худшему файлу:")
    worst = results[0]
    print(f"  📄 {worst['path']}")
    for category, items in sorted(worst["findings"].items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        print(f"\n  [{category}] — {len(items)} нарушений:")
        for item in items[:3]:
            print(f"    • «{item['word']}» → {item['fix']}")
            print(f"      {item['context'][:100]}")

    print_hint("Для исправления запустите: python tools/checkers/check-religionisms.py --fix")
    print_hint("Ручная проверка контекста обязательна — не все маркеры требуют замены")

    return 0


if __name__ == "__main__":
    sys.exit(main())