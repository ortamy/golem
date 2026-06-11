#!/usr/bin/env python3
# tools/checkers/check-exposure.py — полная проверка текста по всем exposure-критериям
import sys
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent))
import argparse
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_warning, print_error, print_hint,
    ask_yes_no, REPO_ROOT
)

SCAN_DIRS = ["terminology", "researches"]
EXCLUDE_DIRS = {"archive", "arkhiv"}
CACHE_FILE = REPO_ROOT / "tools" / "cache" / "exposure-cache.json"

# =============================================================================
# МАРКЕРЫ ИСКАЖЕНИЙ
# =============================================================================

CATEGORY_SUBSTITUTION = [
    (r'\bзакон\b', "Тора = наставление, не закон"),
    (r'\bцерковь\b', "קהילה = собрание, не организация"),
    (r'\bхрам\b', "מקדש = место отделённости, не здание"),
    (r'\bсвященник\b', "כהן = служитель, не иерархический сан"),
    (r'\bзавет\b', "ברית = союз, не договор"),
]

JURIDIFICATION = [
    (r'\bгрех\b', "חטא = промах, не преступление"),
    (r'\bпокаяние\b', "תשובה = возвращение, не юридическое прощение"),
    (r'\bискупление\b', "כפרה = выкуп, не юридическая сделка"),
    (r'\bоправдание\b', "צדקה = справедливость, не вердикт"),
]

PSYCHOLOGIZATION = [
    (r'\bвера\b', "אמונה = верность в делах, не внутреннее чувство"),
    (r'\bстрах Божий\b', "יראת יהוה = трепет-видение, не эмоция страха"),
    (r'\bсмирение\b', "ענווה = готовность учиться, не самоуничижение"),
    (r'\bлюбовь\b', "אהבה = действие, не только эмоция"),
]

ACTION_TO_EMOTION = [
    (r'\bмилость\b', "חסד = преданная любовь в действии, не жалость"),
    (r'\bблагодать\b', "חן = благоволение, не абстрактная 'благодать'"),
    (r'\bмилосердие\b', "רחמים = действие милосердия, не чувство"),
    (r'\bсострадание\b', "רחמים = от רחם (матка), родственная забота в действии"),
]

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

MEANING_NARROWING = [
    (r'\bмилостыня\b', "צדקה = восстановление справедливости, не только подаяние"),
    (r'\bпророк\b', "נביא = призванный вестник, не предсказатель"),
    (r'\bангел\b', "מלאך = вестник (может быть человеком), не крылатое существо"),
    (r'\bкрещение\b', "טבילה = погружение, не ритуал"),
    (r'\bевангелие\b', "בשורה = благая весть, не книга"),
    (r'\bапостол\b', "שליח = посланник, не титул"),
]

DUALIZATION = [
    (r'\bветхий завет\b', "ТаНаХ — не 'ветхий', это живое слово"),
    (r'\bновый завет\b', "ברית חדשה = обновлённый союз, не 'новый' против 'старого'"),
    (r'\bзакон и благодать\b', "Тора и חן — не противоположности"),
    (r'\bдух и плоть\b', "רוח и בשר — оба от Яхве, не враги"),
]

TRANSLITERATION_TRAPS = [
    (r'\bдьявол\b', "διάβολος = клеветник, не имя"),
    (r'\bсатана\b', "שטן = противник/обвинитель, не имя"),
    (r'\bепископ\b', "ἐπίσκοπος = надзиратель, не сан"),
    (r'\bдиакон\b', "διάκονος = служитель, не сан"),
    (r'\bлитургия\b', "λειτουργία = служение, не ритуал"),
    (r'\bевхаристия\b', "εὐχαριστία = благодарение, не таинство"),
    (r'\bлогос\b', "λόγος = слово/дело (דבר), не философский 'Логос'"),
]

NAME_SUBSTITUTION = [
    (r'\bГоспод[ьяуе]?\b', "יהוה = Яхве"),
    (r'\bБог[ауе]?\b', "אלוהים или יהוה"),
    (r'\bХрист[ао]с?\b', "משיח = Машиах (Помазанник)"),
    (r'\bИисус[ае]?\b', "יהושע = Йешуа"),
    (r'\bВсевышний\b', "עליון = Эльйон, или יהוה = Яхве"),
    (r'\bАдонай\b', "יהוה = Яхве; Адонай — традиционная замена"),
]

FINANCIAL_SLAVERY = [
    (r'\bипотека\b', "mortgage = мёртвый залог; шмита = прощение долгов"),
    (r'\bкредит\b', "кредит ↔ шмита (прощение каждые 7 лет)"),
    (r'\bпроцент\b', "процент запрещён в Торе (Шмот 22:24)"),
    (r'\bпенсия\b', "пенсия ↔ йовель (возвращение земли каждые 50 лет)"),
]

ALL_MARKERS = {
    "Подмена категории": CATEGORY_SUBSTITUTION,
    "Юридизация": JURIDIFICATION,
    "Психологизация": PSYCHOLOGIZATION,
    "Действие→эмоция": ACTION_TO_EMOTION,
    "Абстракция": ABSTRACTION,
    "Сужение смысла": MEANING_NARROWING,
    "Дуализация": DUALIZATION,
    "Транслитерация": TRANSLITERATION_TRAPS,
    "Имя→титул": NAME_SUBSTITUTION,
    "Финансовое рабство": FINANCIAL_SLAVERY,
}

# Белый список контекстов (не заменять)
WHITELIST_CONTEXTS = [
    r'закон Моше', r'закон Торы', r'закон Яхве',
    r'цитата', r'синодальный', r'перевод',
]

# =============================================================================
# ФУНКЦИИ
# =============================================================================

def protect_content(content):
    """Защищает блоки кода, иврит, цитаты от проверки."""
    protected = content
    # Блоки кода
    protected = re.sub(r'```.*?```', ' ', protected, flags=re.DOTALL)
    # Инлайн-код
    protected = re.sub(r'`[^`]+`', ' ', protected)
    # Иврит
    protected = re.sub(r'[\u0590-\u05FF]{2,}', ' ', protected)
    # Цитаты в кавычках
    protected = re.sub(r'«[^»]*»', ' ', protected)
    # Белый список контекстов
    for ctx in WHITELIST_CONTEXTS:
        protected = re.sub(ctx, ' ', protected, flags=re.IGNORECASE)
    return protected


def load_cache():
    """Загружает кеш проверок."""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
        except:
            pass
    return {}


def save_cache(cache):
    """Сохраняет кеш проверок."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')


def check_file(filepath: Path, cache: dict) -> dict:
    """Проверяет один файл по всем маркерам."""
    rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
    mtime = filepath.stat().st_mtime

    # Кеш
    if rel_path in cache and cache[rel_path].get('mtime') == mtime:
        cached = cache[rel_path]
        if 'findings' in cached and cached['findings']:
            return {"path": rel_path, "findings": cached['findings']}
        elif 'findings' in cached:
            return None

    content = read_file_safe(filepath)
    if not content:
        return None

    clean = protect_content(content)
    findings = defaultdict(list)

    for category, markers in ALL_MARKERS.items():
        for pattern, fix in markers:
            for match in re.finditer(pattern, clean, re.IGNORECASE):
                word = match.group()
                start = max(0, match.start() - 30)
                end = min(len(clean), match.end() + 30)
                context = clean[start:end].replace('\n', ' ').strip()
                findings[category].append({
                    "word": word,
                    "context": f"...{context}...",
                    "fix": fix
                })

    # Обновляем кеш
    cache[rel_path] = {"mtime": mtime}
    if findings:
        cache[rel_path]["findings"] = dict(findings)
        return {"path": rel_path, "findings": dict(findings)}

    return None


def fix_file(filepath: Path, findings: dict) -> int:
    """Заменяет маркеры на правильные термины."""
    content = read_file_safe(filepath)
    if not content:
        return 0

    fixes = 0
    for category, items in findings.items():
        for item in items:
            word = item["word"]
            fix = item["fix"]
            # Берём только первое предложение fix (до запятой или точки)
            replacement = fix.split(",")[0].split(".")[0].strip()
            # Если fix содержит " = " — берём то что слева
            if " = " in replacement:
                replacement = replacement.split(" = ")[0].strip()

            # Не заменяем если слово в белом списке
            if any(re.search(ctx, content, re.IGNORECASE) for ctx in WHITELIST_CONTEXTS):
                continue

            # Заменяем только если это не часть другого слова
            new_content = re.sub(rf'\b{re.escape(word)}\b', replacement, content, count=1)
            if new_content != content:
                content = new_content
                fixes += 1

    if fixes > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    return fixes


def save_report(results, output_path=None):
    """Сохраняет отчёт."""
    if not output_path:
        output_path = REPO_ROOT / "reports" / f"exposure-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    output_path.parent.mkdir(exist_ok=True)

    lines = [
        f"# 🔍 EXPOSURE-ОТЧЁТ",
        f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Файлов с нарушениями:** {len(results)}",
        "",
    ]

    # По категориям
    cat_stats = Counter()
    for r in results:
        for cat in r["findings"]:
            cat_stats[cat] += len(r["findings"][cat])

    lines.append("## 📊 По категориям")
    for cat, count in cat_stats.most_common():
        lines.append(f"- **{cat}**: {count}")
    lines.append("")

    # По файлам
    results_sorted = sorted(results, key=lambda r: sum(len(v) for v in r["findings"].values()), reverse=True)
    lines.append(f"## 📋 Файлы ({len(results)})")
    for r in results_sorted:
        total = sum(len(v) for v in r["findings"].values())
        lines.append(f"- **{r['path']}** — {total} маркеров")
        for cat, items in sorted(r["findings"].items(), key=lambda x: len(x[1]), reverse=True)[:3]:
            lines.append(f"  - {cat}: {len(items)}")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return output_path


def main():
    fix_mode = "--fix" in sys.argv
    save_mode = "--save" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    top_n = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 10

    print_header("ПОЛНАЯ ПРОВЕРКА ПО EXPOSURE", "🔍")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            for f in sorted(dir_path.rglob("*.md")):
                if not any(excl in str(f) for excl in EXCLUDE_DIRS):
                    all_files.append(f)

    total = len(all_files)
    print(f"🔍 Файлов: {total}")
    print(f"📋 Категорий: {len(ALL_MARKERS)}")
    print(f"📍 Маркеров: {sum(len(v) for v in ALL_MARKERS.values())}")

    cache = load_cache()
    results = []
    total_markers = 0
    cat_stats = Counter()
    total_fixed = 0

    for i, filepath in enumerate(all_files, 1):
        result = check_file(filepath, cache)
        if result:
            if fix_mode:
                fixed = fix_file(filepath, result["findings"])
                if fixed:
                    total_fixed += fixed
                    # Перепроверяем
                    cache.pop(str(filepath.relative_to(REPO_ROOT)).replace('\\', '/'), None)
                    result = check_file(filepath, cache)
                    if not result:
                        continue

            results.append(result)
            for cat in result["findings"]:
                count = len(result["findings"][cat])
                total_markers += count
                cat_stats[cat] += count

        extra = f"маркеров: {total_markers}"
        if fix_mode:
            extra += f" | исправлено: {total_fixed}"
        progress_bar(i, total, extra=extra)

    finish_progress()
    save_cache(cache)

    if fix_mode:
        print_success(f"🔧 Исправлено: {total_fixed}")

    if not results:
        print_success("🎉 Нарушений не найдено — текст чист по всем exposure-критериям")
        return 0

    print(f"\n📁 Файлов с нарушениями: {len(results)}")
    print(f"📝 Всего маркеров: {total_markers}\n")

    print("📊 По категориям:")
    for cat, count in cat_stats.most_common():
        bar = "█" * min(count, 30)
        print(f"  {cat:25} {count:4}  {bar}")

    # Топ файлов
    results.sort(key=lambda r: sum(len(v) for v in r["findings"].values()), reverse=True)
    print(f"\n📋 Худшие файлы (топ {top_n}):")
    for r in results[:top_n]:
        total = sum(len(v) for v in r["findings"].values())
        top_cat = max(r["findings"], key=lambda k: len(r["findings"][k]))
        print(f"  • {r['path']} — {total} ({top_cat} ×{len(r['findings'][top_cat])})")

    # Детали по худшему
    if verbose and results:
        worst = results[0]
        print(f"\n🔍 Детали: {worst['path']}")
        for cat, items in sorted(worst["findings"].items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            print(f"\n  [{cat}] — {len(items)}:")
            for item in items[:3]:
                print(f"    • «{item['word']}» → {item['fix']}")
                print(f"      {item['context'][:100]}")

    if save_mode:
        report_path = save_report(results)
        print_success(f"\nОтчёт сохранён: {report_path}")

    if not fix_mode and total_markers > 0:
        if ask_yes_no("\n🔧 Запустить автофикс?"):
            cache = load_cache()
            fixed = 0
            for r in results:
                filepath = REPO_ROOT / r["path"]
                f = fix_file(filepath, r["findings"])
                fixed += f
            print_success(f"Исправлено: {fixed}")
            save_cache(cache)

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())