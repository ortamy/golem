# tools/checkers/check-file-names-language.py — проверка чистоты языка имён файлов (v5.0 FINAL)
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_hint, REPO_ROOT

SCAN_DIRS = ["terminology", "researches"]

# =============================================================================
# ИВРИТСКИЕ ПАТТЕРНЫ (всё что является ивритом)
# =============================================================================
HEBREW_PARTS = {
    # Служебные частицы (предлоги, артикли, союзы)
    "ha", "va", "be", "ba", "la", "le", "ka", "ke", "ve", "u",
    "me", "mi", "she", "et", "al", "el", "ad", "im", "lo",
    # Короткие ивритские слова
    "el", "ra", "tov", "or", "tam", "shem", "lev", "ben", "bat",
    "av", "em", "yam", "yad", "rosh", "ish", "isha", "bayit",
    "eretz", "am", "goy", "torah", "mitz", "ahav", "shir",
    # Полные слова
    "avar", "atid", "beit", "mikdash", "emuna", "etz", "daat",
    "kohen", "hagadol", "lashon", "kodesh", "mene", "tekel",
    "tohu", "vohu", "yhwh", "yir", "palaestina", "satan",
    "nachash", "nefesh", "ruach", "chesed", "tzedek", "shalom",
    "shabbat", "torah", "melech", "navi", "koach", "kavod",
    "brit", "mishpat", "mishkan", "mikveh", "korban", "tefilah",
    "tshuva", "tvilah", "yeshuah", "yovel", "sheerit", "shekel",
    "sheol", "shmitah", "olam", "levav", "levad", "lamad",
    "nefesh", "neshamah", "nishmah", "naaf", "ivri", "golem",
    "gibor", "eved", "emet", "arur", "arum", "asur", "avon",
    "cherut", "chamas", "barach", "bavel", "gerim", "goyim",
    "heichal", "het", "karet", "kehillah", "malach", "mashiah",
    "midbar", "mishchah", "nicham", "niddah", "panim", "pesel",
    "rapha", "resha", "zarak", "zera",
    # Ивритские паттерны (для автоопределения)
    "ch", "sh", "tz", "ah", "eh", "ih", "oh", "uh", "kh",
    "im", "ot", "ut", "av", "ev", "iv", "et", "it",
    "yah", "yahu", "yir", "derech", "hevel", "shamayim",
}

# =============================================================================
# ТОЧНО НЕ ИВРИТ
# =============================================================================
NON_HEBREW = {
    # Английские слова
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her",
    "was", "one", "our", "out", "has", "have", "from", "they", "this", "that",
    "with", "will", "been", "were", "some", "what", "when", "your", "which",
    "their", "time", "about", "would", "could", "should", "there", "these",
    "those", "after", "before", "under", "over", "into", "onto", "upon",
    "people", "world", "life", "death", "love", "hate", "good", "evil",
    "power", "money", "water", "earth", "light", "dark", "fire", "wind",
    "history", "system", "truth", "faith", "hope", "peace", "order", "war",
    "first", "last", "next", "more", "less", "most", "least",
    "human", "woman", "child", "place", "thing", "point", "part",
    "body", "mind", "heart", "soul", "spirit", "flesh", "blood",
    "house", "home", "land", "king", "lord", "god", "book", "word",
    "sun", "moon", "star", "tree", "seed", "fruit", "bread", "wine",
    "science", "psychology", "medicine", "economy", "politics",
    "sociology", "media", "sport", "language", "teaching",
    "origin", "theory", "myth", "ritual", "control", "strategy",
    "support", "structure", "research", "analysis", "distortion",
    "comparison", "slavery", "temple", "study", "method", "practice",
    "principle", "concept", "process", "project", "problem", "solution",
    "ism", "ity", "ion", "ing", "ment", "ness", "ship",
    # Имена собственные
    "paracelsus", "hippocrates", "einstein", "newton", "darwin",
    "freud", "jung", "platon", "aristotle", "socrates",
    "ibm", "google", "amazon", "apple", "microsoft", "facebook", "meta",
    "blackrock", "vanguard", "goldman", "jpmorgan", "palantir", "neuralink",
    "helena", "natasha", "ortam", "kissinger", "machiavelli", "hitler",
    "budda", "mohammed", "confucius", "lao", "zarathustra",
    "pornography", "pedophilia", "psychology", "sociology",
    # Библейские грецизмы/латинизмы
    "abracadabra", "apocalypse", "armageddon", "exorcism",
    "resurrection", "catholic", "orthodox", "protestant",
    "nicaea", "trinity", "christ", "jesus", "baptism",
    "eucharist", "liturgy", "diocese", "patriarch",
    "adonai", "balaam", "beelzebub", "golgotha", "gehenna",
    "mammon", "messiah", "satan", "cherub", "seraph",
    # Русские корни (транслит)
    "pravoslav", "hristian", "katolic", "klerikal", "lyucifer",
    "mormon", "pyatidesyat", "farisei", "kabbal",
    "talmud", "rabbin", "masson", "mason", "fash", "kommun",
    "social", "capital", "totalitar", "colonial",
    "slavs", "slavic", "slav", "russian", "soviet",
    # Английские слова с ивритскими паттернами (ложные срабатывания)
    "pyramid", "sachs", "goldman", "religion", "hacker",
    "karaism", "palaestina", "satan", "not", "support",
    "bunker", "history", "religion",
}


def part_is_hebrew(part: str) -> bool:
    """Проверяет, является ли часть имени ивритским словом."""
    if part in NON_HEBREW:
        return False
    if part in HEBREW_PARTS:
        return True
    if len(part) <= 2:
        return False
    # Проверяем ивритские паттерны
    for pattern in HEBREW_PARTS:
        if len(pattern) >= 3 and (pattern in part.lower() or part.lower() == pattern):
            return True
    return False


def part_is_english(part: str) -> bool:
    """Проверяет, является ли часть имени английским словом."""
    if part in NON_HEBREW:
        return True
    if part in HEBREW_PARTS:
        return False
    # Нет ивритских паттернов
    for pattern in HEBREW_PARTS:
        if len(pattern) >= 3 and pattern in part.lower():
            return False
    return True


def analyze_name(stem: str) -> dict:
    """Анализирует имя файла."""
    if re.search(r'[а-яё]', stem, re.IGNORECASE):
        return {"type": "russian", "clean": False}

    parts = stem.split('-')
    hebrew_parts = []
    english_parts = []

    for part in parts:
        if part_is_hebrew(part):
            hebrew_parts.append(part)
        elif part_is_english(part):
            english_parts.append(part)
        else:
            english_parts.append(part)

    if hebrew_parts and english_parts:
        return {"type": "mixed", "hebrew": hebrew_parts, "english": english_parts, "clean": False}
    elif hebrew_parts:
        return {"type": "hebrew", "clean": True}
    else:
        return {"type": "english", "clean": True}


def check_file(filepath: Path) -> dict:
    content = read_file_safe(filepath)
    if not content:
        return None

    stem = filepath.stem
    rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
    parts = rel_path.split('/')
    is_terminology = parts[0] == "terminology"
    is_tanakh = len(parts) >= 2 and parts[-2] == "tanakh"

    analysis = analyze_name(stem)
    issues = []

    if is_terminology or is_tanakh:
        if analysis["type"] == "mixed":
            issues.append(f"смесь: иврит ({', '.join(analysis['hebrew'])}) + англ ({', '.join(analysis['english'])})")
        elif analysis["type"] == "english":
            issues.append(f"английское имя: '{stem}'")
        elif analysis["type"] == "russian":
            issues.append(f"русские буквы: '{stem}'")
    else:
        if analysis["type"] == "mixed":
            issues.append(f"смесь: иврит ({', '.join(analysis['hebrew'])}) + англ ({', '.join(analysis['english'])})")
        elif analysis["type"] == "hebrew":
            issues.append(f"иврит в не-танах: '{stem}'")
        elif analysis["type"] == "russian":
            issues.append(f"русские буквы: '{stem}'")

    if issues:
        return {"path": rel_path, "issues": issues, "type": analysis["type"]}

    return None


def main():
    fix_mode = "--fix" in sys.argv

    print_header("ПРОВЕРКА ЧИСТОТЫ ЯЗЫКА ИМЁН", "🏷️")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    print(f"Найдено файлов: {total}")

    issues_found = []

    for i, filepath in enumerate(all_files, 1):
        result = check_file(filepath)
        if result:
            issues_found.append(result)
        progress_bar(i, total, extra=f"проблем: {len(issues_found)}")

    finish_progress()

    if not issues_found:
        print_success("Все имена файлов чистые")
        return 0

    print_warning(f"Файлов с проблемами: {len(issues_found)}")

    stats = defaultdict(int)
    for result in issues_found:
        for issue in result["issues"]:
            if "русские" in issue: stats["русские буквы"] += 1
            elif "смесь" in issue: stats["смесь языков"] += 1
            elif "иврит в не-танах" in issue: stats["иврит в не-танах"] += 1
            elif "английское" in issue: stats["англ в танахе"] += 1

    print("\n📊 Типы проблем:")
    for t, c in sorted(stats.items()):
        print(f"   {t}: {c}")

    if len(issues_found) <= 30:
        print(f"\n📋 Все файлы:")
        for result in issues_found:
            print(f"\n  📄 {result['path']}")
            for issue in result["issues"]:
                print(f"    • {issue}")
    else:
        print(f"\n📋 Первые 20 из {len(issues_found)}:")
        for result in issues_found[:20]:
            print(f"\n  📄 {result['path']}")
            for issue in result["issues"]:
                print(f"    • {issue}")
        print(f"\n  ... и ещё {len(issues_found) - 20}")

    print()
    print_hint("Иврит → переместите в tanakh/ (sort-files.py)")
    print_hint("Английский в танахе → переместите из tanakh/")
    print_hint("Смесь → переименуйте в чистое имя")

    return 0


if __name__ == "__main__":
    sys.exit(main())

