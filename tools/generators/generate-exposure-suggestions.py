#!/usr/bin/env python3
# tools/generators/generate-exposure-suggestions.py — поиск кандидатов на новые методы/приёмы (v3)
import sys
import re
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_warning, print_hint,
    REPO_ROOT
)

SCAN_DIRS = ["researches", "terminology"]
EXCLUDE_DIRS = {"archive", "arkhiv", "religionizmy"}
EXPOSURE_DIR = REPO_ROOT / "instructions" / "exposure"

SUBSTITUTION_PATTERNS = [
    (r'(?:в оригинале|в иврите|в ТаНаХе)\s+«?([^»]+?)»?\s*[→–—]\s*«?([^»]+?)»?', 'оригинал→перевод', 10),
    (r'(?:подмена|замена)\s+(\w+(?:\s+\w+){0,3})\s*(?:→|на)\s*(\w+(?:\s+\w+){0,3})', 'подмена', 8),
    (r'вместо\s+«?([^»]+?)»?\s*(?:—|→|–)\s*«?([^»]+?)»?', 'вместо', 5),
    (r'система\s+(заменяет|подменяет|превращает)\s+(\w+(?:\s+\w+){0,5})', 'система', 3),
]

TANAKH_WORDS = {
    'яхве', 'yhwh', 'элоhим', 'эль', 'тора', 'танах', 'машиах', 'шаббат',
    'нэфеш', 'руах', 'шеол', 'брит', 'кодеш', 'эмуна', 'тшува', 'цдака',
    'хесед', 'эмет', 'шалом', 'коhэн', 'нави', 'микдаш', 'кеhила',
    'давар', 'хохма', 'йешуа', 'моше', 'цадик', 'корбан', 'тамэ', 'таhор',
}

SYSTEM_WORDS = {
    'бог', 'господь', 'душа', 'дух', 'вера', 'грех', 'покаяние', 'спасение',
    'закон', 'церковь', 'храм', 'священник', 'дьявол', 'крещение',
    'милость', 'благодать', 'истина', 'завет', 'искупление', 'ад', 'рай',
    'религия', 'духовность', 'физика', 'математика', 'технология',
}


def load_existing_techniques():
    existing = set()
    for fname in ["exposure-techniques.md", "exposure-distortions.md",
                   "exposure-language.md", "exposure-mechanisms.md",
                   "exposure-methods.md", "exposure-religionism.md"]:
        filepath = EXPOSURE_DIR / fname
        if not filepath.exists():
            continue
        content = read_file_safe(filepath)
        if not content:
            continue
        for line in content.splitlines():
            line = line.strip()
            if line.startswith('- **') or line.startswith('- '):
                existing.update(re.findall(r'[а-яё]{4,}', line.lower()))
    return existing


def is_noise(candidate: dict) -> bool:
    text = candidate["match"] + " " + candidate["context"]
    if re.search(r'</?td>|</?tr>|</?table>|</?strong>', text):
        return True
    uppercase_count = sum(1 for c in text if c.isupper())
    if uppercase_count > len(text) * 0.3:
        return True
    if candidate["type"] == "вместо":
        words = set(re.findall(r'\w+', text.lower()))
        if not (words & TANAKH_WORDS or words & SYSTEM_WORDS):
            return True
    return False


def find_candidates(filepath: Path) -> list:
    content = read_file_safe(filepath)
    if not content:
        return []
    rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
    candidates = []
    for pattern, ptype, priority in SUBSTITUTION_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            groups = match.groups()
            context = content[max(0, match.start()-60):match.end()+60].replace('\n', ' ').strip()
            c = {
                "file": rel_path,
                "type": ptype,
                "priority": priority,
                "match": match.group(),
                "context": f"...{context}...",
                "groups": groups,
            }
            if not is_noise(c):
                candidates.append(c)
    return candidates


def is_new_candidate(candidate: dict, existing: set, found_matches: set) -> bool:
    match_lower = candidate["match"].lower()
    words = set(re.findall(r'[а-яё]{4,}', match_lower))
    if len(words & existing) >= len(words) * 0.5:
        return False
    if match_lower in found_matches:
        return False
    return True


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print_header("ПОИСК НОВЫХ ПРИЁМОВ", "🔍")

    existing = load_existing_techniques()
    print(f"📚 Маркеров: {len(existing)}")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            for f in sorted(dir_path.rglob("*.md")):
                if not any(excl in f.relative_to(REPO_ROOT).parts for excl in EXCLUDE_DIRS):
                    all_files.append(f)

    total = len(all_files)
    print(f"🔍 Файлов: {total}")

    all_candidates = []
    found_matches = set()
    stats = Counter()
    by_file = defaultdict(list)

    for i, filepath in enumerate(all_files, 1):
        for c in find_candidates(filepath):
            if is_new_candidate(c, existing, found_matches):
                all_candidates.append(c)
                found_matches.add(c["match"].lower())
                stats[c["type"]] += 1
                by_file[c["file"]].append(c)
        progress_bar(i, total, extra=f"кандидатов: {len(all_candidates)}")

    finish_progress()

    if not all_candidates:
        print_success("Новых кандидатов не найдено")
        return 0

    # Компактный вывод
    print(f"\n📝 Кандидатов: {len(all_candidates)}")
    print(f"📊 Типы: {' | '.join(f'{t}: {c}' for t, c in stats.most_common())}")

    print(f"\n📋 Топ файлов:")
    for filepath, cands in sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)[:8]:
        cands.sort(key=lambda x: x["priority"], reverse=True)
        types_in_file = Counter(c["type"] for c in cands)
        top_match = cands[0]["match"][:60]
        print(f"  {filepath}: {len(cands)} | {' '.join(f'{t}×{c}' for t,c in types_in_file.most_common(2))} | {top_match}...")

    # Подробно только при --verbose
    if verbose:
        print(f"\n📋 Все кандидаты (сортированы по приоритету):")
        all_candidates.sort(key=lambda x: x["priority"], reverse=True)
        for c in all_candidates:
            print(f"  [{c['priority']}] {c['type']}: {c['match']}")
            print(f"     📄 {c['file']}")
    else:
        print_hint("\n--verbose для полного списка")

    # Сохраняем
    output = REPO_ROOT / "neural" / "training-data" / "exposure-candidates.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump({"total": len(all_candidates), "stats": dict(stats), "candidates": all_candidates}, f, ensure_ascii=False, indent=2)

    print_success(f"\nСохранено: {output}")
    print_hint("AI-анализ: python neural/inference/client.py --analyze-exposure")

    return 0


if __name__ == "__main__":
    sys.exit(main())