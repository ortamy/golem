# tools/automation/sort-files.py — интеллектуальная сортировка файлов (v4.5)
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_hint, ask_yes_no, REPO_ROOT

TARGET_BASE = REPO_ROOT / "researches"

# =============================================================================
# ИВРИТСКИЕ ПАТТЕРНЫ (для автоопределения tanakh/)
# =============================================================================
HEBREW_PATTERNS = [
    "ch", "sh", "tz", "ah", "eh", "ih", "oh", "uh", "kh",
    "im", "ot", "ut", "av", "ev", "iv", "ah", "et", "it",
    "ha-", "be-", "le-", "ke-", "mi-", "ve-", "she-",
    "el", "yah", "yahu", "yir", "derech", "nachash", "hevel",
    "chesed", "emunah", "tzedek", "ruach", "nefesh", "shem",
    "shamayim", "olam", "barach", "lev", "koach", "melech", "navi",
    "kodesh", "mish", "brit", "korban", "shab", "shalom",
    "tefil", "tshuva", "tvilah", "yeshu", "yhwh", "yovel", "zera",
    "mitz", "mish", "mik", "mid", "min", "mak", "mal",
    "nish", "nich", "nid", "naf", "nesh", "nef",
    "rach", "raph", "resh", "ruc", "shaal", "shee", "shle",
    "tzed", "tzoh", "tzev", "yeg", "yir", "yov",
    "arum", "arur", "asur", "avon", "emet", "eved",
    "gibor", "golem", "ivri", "karet", "kavod", "lamad", "levad",
    "levav", "naaf", "nefe", "olam", "panim", "pesel", "raph",
    "sata", "tov", "tzed", "yetz", "zarak", "zera",
    "kohen", "koach", "kodesh", "korban", "malach", "melech",
    "mikveh", "mishkan", "mishpat", "navi", "nefesh", "neshamah",
    "ruach", "shabbat", "shalom", "sheerit", "shekel",
    "sheol", "shmitah", "tefilah", "torah", "tshuva",
    "tvilah", "tzedek", "yeshuah", "yovel",
]

# Не-иврит (английские слова, имена, библейские грецизмы)
NON_HEBREW = {
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
    "sociology", "media", "sport", "language", "history", "teaching",
    "origin", "theory", "myth", "ritual", "control", "strategy",
    # Имена собственные
    "paracelsus", "hippocrates", "einstein", "newton", "darwin",
    "freud", "jung", "platon", "aristotle", "socrates",
    "ibm", "google", "amazon", "apple", "microsoft", "facebook", "meta",
    "blackrock", "vanguard", "goldman", "jpmorgan", "palantir", "neuralink",
    "helena", "natasha", "ortam", "kissinger", "machiavelli", "hitler",
    "budda", "mohammed", "confucius", "lao", "zarathustra",
    "pornography", "pedophilia", "psychology", "sociology",
    # Библейские понятия (греческие/латинские — НЕ иврит)
    "abracadabra", "apocalypse", "armageddon", "exorcism",
    "resurrection", "catholic", "orthodox", "protestant",
    "nicaea", "trinity", "christ", "jesus", "baptism",
    "eucharist", "liturgy", "diocese", "patriarch",
    "adonai", "balaam", "beelzebub", "golgotha", "gehenna",
    "mammon", "messiah", "satan", "cherub", "seraph",
    # Полу-иврит (иврит + английский = не чистый иврит)
    "adonai-origin", "balaam-strategy", "bashah-structure",
    "dam-yeshua-seal", "hebrew-vs-languages", "hebrew-truth",
    "hebrew-week", "hebrew-creational", "hellenization-vs-hebraization",
    "loss-in-translation", "march-8-history", "masoretic-text",
    "missing-hebrew-scrolls", "paleo-hebrew", "prayer-distortion",
    "purpose-of-tanakh", "resurrection-analysis", "secta-meaning",
    "serpent-healing", "slavic-substrate", "substitution-of-the-name",
    "tanakh-not-old-testament", "tree-language", "why-canaan-land",
    "why-people-cant-agree", "yehoshua-research",
}


def is_hebrew_name(stem: str) -> bool:
    """Проверяет, является ли имя файла ивритским."""
    if stem in NON_HEBREW:
        return False
    if not re.match(r'^[a-z]+(-[a-z]+)*$', stem):
        return False

    parts = stem.split('-')
    for part in parts:
        if part in NON_HEBREW:
            return False
        if len(part) <= 2:
            continue
        found = False
        for pattern in HEBREW_PATTERNS:
            if pattern in part.lower() or part.lower() == pattern:
                found = True
                break
        if not found:
            return False

    return True


def determine_category(filepath: Path) -> str:
    stem = filepath.stem

    # 1. Ивритские имена → tanakh
    if is_hebrew_name(stem):
        return "tanakh"

    # 2. Контекстный анализ
    content = read_file_safe(filepath)
    if not content:
        return "archive"

    lines = content.split('\n')
    title_line = topic_line = ""
    body_start = 0

    for i, line in enumerate(lines):
        if line.startswith('# ') and not title_line:
            title_line = line
        if '**Тема:**' in line and not topic_line:
            topic_line = line
        if body_start == 0 and (line.startswith('## ') or line.startswith('---')):
            body_start = i

    title_and_topic = (title_line + " " + topic_line).lower()
    body = '\n'.join(lines[body_start:]).lower() if body_start else content.lower()
    filename = stem.lower()
    scores = defaultdict(float)

    CATEGORY_RULES = {
        "systems": (1.0, [
            "система", "system", "религионизм", "religionism",
            "мицраим", "mitzraim", "вавилон", "bavel", "babel", "babylon",
            "рим", "rome", "колизей", "coliseum",
            "империя", "empire", "власть", "power", "контроль", "control",
            "фашизм", "fashizm", "коммунизм", "kommunizm",
            "капитализм", "capitalism", "социализм", "socializm",
            "тоталитар", "totalitar", "масон", "mason",
            "государств", "state system", "политическ", "political system",
            "рабство", "slavery", "порабощ", "enslav",
            "колониализм", "colonialism", "иго", "yoke",
            "апокалипсис", "apocalypse", "пирамида", "pyramid", "бункер", "bunker",
        ]),
        "teachings": (1.0, [
            "учение", "teaching", "доктрина", "doctrine",
            "религия", "religion", "культ", "cult", "секта", "sect", "ересь", "heresy",
            "философия", "philosophy", "идеология", "ideology",
            "буддизм", "buddhism", "индуизм", "hinduism",
            "ислам", "islam", "мусульман", "muslim",
            "христианств", "christianity", "иудаизм", "judaism",
            "католицизм", "catholicism", "православи", "orthodox", "протестант", "protestant",
            "талмуд", "talmud", "каббала", "kabbalah", "раввинизм", "rabbinic",
            "сатанизм", "satanism", "оккультизм", "occultism",
            "магия", "magic", "колдовство", "witchcraft",
            "гностицизм", "gnosticism", "платонизм", "platonism",
            "язычество", "paganism", "шаманизм", "shamanism",
            "монотеизм", "monotheism", "политеизм", "polytheism",
            "никейский", "nicaea", "собор", "council",
        ]),
        "psychology": (1.0, [
            "психология", "psychology", "психика", "psyche",
            "сознание", "consciousness", "мышление", "thinking",
            "разум", "mind", "мозг", "brain",
            "эмоция", "emotion", "травма", "trauma", "депрессия", "depression",
            "манипуляция", "manipulation", "гипноз", "hypnosis",
        ]),
        "science": (1.0, [
            "наука", "science", "эволюция", "evolution",
            "генетика", "genetics", "биология", "biology",
            "физика", "physics", "квантов", "quantum",
        ]),
        "medicine": (1.0, [
            "медицина", "medicine", "здоровье", "health", "болезнь", "disease",
            "лекарство", "drug", "фармацевт", "pharmaceutical",
            "вакцина", "vaccine", "больница", "hospital", "врач", "doctor",
            "вирус", "virus", "рак", "cancer", "исцеление", "healing",
        ]),
        "economy": (1.0, [
            "экономика", "economy", "финансы", "finance",
            "деньги", "money", "валюта", "currency",
            "банк", "bank", "кредит", "credit", "долг", "debt",
            "капитал", "capital", "рынок", "market",
            "богатство", "wealth", "бедность", "poverty",
            "ростовщик", "usury", "процент", "interest",
        ]),
        "politics": (1.0, [
            "политика", "politics", "государство", "state",
            "правительство", "government", "партия", "party",
            "демократия", "democracy", "диктатура", "dictatorship",
            "монархия", "monarchy", "война", "war", "армия", "army",
        ]),
        "history": (1.0, [
            "история", "history", "древний", "ancient",
            "средневековье", "medieval", "цивилизация", "civilization",
            "археология", "archeology", "кумран", "qumran", "свитки", "scrolls",
            "крестовые", "crusades", "инквизиция", "inquisition",
            "реформация", "reformation", "холокост", "holocaust",
        ]),
        "sociology": (1.0, [
            "общество", "society", "социальный", "social",
            "социология", "sociology", "община", "community",
            "семья", "family", "брак", "marriage",
            "традиция", "tradition", "культура", "culture",
            "этнос", "ethnic", "народ", "people", "нация", "nation",
        ]),
        "media": (1.0, [
            "медиа", "media", "социальные сети", "social media",
            "интернет", "internet", "цифровой", "digital",
            "алгоритм", "algorithm", "сми", "mass media",
            "кино", "cinema", "реклама", "advertising",
            "пропаганда", "propaganda", "виртуальный", "virtual",
        ]),
        "language": (0.6, [
            "иврит", "hebrew", "арамейский", "aramaic",
            "греческий", "greek", "латынь", "latin",
            "перевод", "translation", "транслитерация", "transliteration",
            "семитский", "semitic", "синтаксис", "syntax",
            "грамматика", "grammar", "этимология", "etymology",
            "масоретский", "masoretic", "септуагинта", "septuagint",
            "вульгата", "vulgate", "пешитта", "peshitta",
            "палео-иврит", "paleo-hebrew", "язык", "language",
        ]),
        "sport": (1.0, [
            "спорт", "sport", "олимпийский", "olympic",
            "футбол", "football", "атлет", "athlete",
            "соревнование", "competition", "стадион", "stadium",
        ]),
    }

    for category, (weight, keywords) in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in title_and_topic:
                scores[category] += weight * 3
            elif keyword in filename:
                scores[category] += weight * 2
            elif keyword in body:
                scores[category] += weight

    if scores:
        best = max(scores, key=scores.get)
        if scores[best] >= 1.0:
            return best

    return "archive"


def get_target_path(filepath: Path, category: str):
    rel_path = filepath.relative_to(REPO_ROOT)
    if len(rel_path.parts) >= 3 and rel_path.parts[1] == category:
        return None
    if len(rel_path.parts) == 2 and rel_path.parts[0] == "researches":
        return TARGET_BASE / category / filepath.name
    return None


def main():
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    print_header("СОРТИРОВКА ФАЙЛОВ ПО КАТЕГОРИЯМ", "📁")

    all_files = []
    for md_file in (REPO_ROOT / "researches").rglob("*.md"):
        rel = md_file.relative_to(REPO_ROOT / "researches")
        if len(rel.parts) == 1:
            all_files.append(md_file)

    total = len(all_files)
    print(f"Найдено файлов в корне researches/: {total}")

    if total == 0:
        print_success("Нет файлов для сортировки")
        return 0

    moves = []
    stats = defaultdict(int)
    archive_files = []

    for i, filepath in enumerate(all_files, 1):
        category = determine_category(filepath)
        target = get_target_path(filepath, category)

        rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')

        if category == "archive":
            archive_files.append(rel_path)

        if target:
            target_rel = str(target.relative_to(REPO_ROOT)).replace('\\', '/')
            moves.append((filepath, target, rel_path, target_rel, category))
            stats[category] += 1

        progress_bar(i, total, extra=f"к перемещению: {len(moves)}")

    finish_progress()

    if archive_files:
        print(f"\n📦 В архив: {len(archive_files)} файлов")
        for path in archive_files[:10]:
            print(f"   • {path}")
        if len(archive_files) > 10:
            print(f"   ... и ещё {len(archive_files) - 10}")

    if not moves:
        print_success("Нечего сортировать")
        return 0

    print(f"\n📊 Категории:")
    for cat, cnt in sorted(stats.items()):
        print(f"   {cat}/ — {cnt}")

    print(f"\n📋 Примеры (первые 15):")
    for _, _, src, dst, _ in moves[:15]:
        print(f"   • {src} → {dst}")
    if len(moves) > 15:
        print(f"   ... и ещё {len(moves) - 15}")

    if dry_run:
        print_hint("Для перемещения: python tools/automation/sort-files.py")
        return 0

    if not force and not ask_yes_no(f"\nПереместить {len(moves)} файлов?"):
        print("👋 Отменено.")
        return 0

    moved, errors = 0, []
    for i, (src, dst, src_rel, dst_rel, _) in enumerate(moves, 1):
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                stem, c = dst.stem, 1
                while dst.exists():
                    dst = dst.parent / f"{stem}-{c}.md"
                    c += 1
            src.rename(dst)
            moved += 1
        except Exception as e:
            errors.append((src_rel, str(e)))
        progress_bar(i, len(moves), extra=f"перемещено: {moved}")

    finish_progress()
    if errors:
        print_warning(f"Ошибок: {len(errors)}")
    print_success(f"Перемещено: {moved} файлов")
    print_hint("Запустите sync-structure.py и check-links.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())