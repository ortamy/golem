#!/usr/bin/env python3
"""
tools/interlinear-generator.py — Генератор подстрочника ТаНаХа (6 строк).

Формат вывода (6 строк на каждый стих, слово-в-слово):
1.  Палео-иврит          (золотой)
2.  Кумран (если есть)   (медный/оранжевый)
3.  Масоретский          (белый)
4.  LXX греческий        (голубой)
5.  Транслитерация       (серый)
6.  Буквальный перевод   (белый)

Использование:
  python tools/interlinear-generator.py "bereshit 1:1-5" --output test-interlinear.html
  python tools/interlinear-generator.py "dvarim 32:8" --output test-qumran.html
"""

import json
import os
import re
import sys
import argparse
import importlib.util
from pathlib import Path

# Пути к файлам
BASE_DIR = Path(__file__).resolve().parent.parent
PALEO_MAP_PATH = BASE_DIR / "tools" / "paleo-map.json"
TRANSLATION_PATH = BASE_DIR / "data" / "translation.json"
QUMRAN_PATH = BASE_DIR / "data" / "qumran.json"
LXX_PATH = BASE_DIR / "data" / "lxx.json"
TANAKH_CACHE_DIR = BASE_DIR / "data" / "tanakh-cache"

# Unicode-диапазоны
HEBREW_LETTERS = set(range(0x05D0, 0x05EB))  # א–ת
NIQQUD_MARKS = set(range(0x0591, 0x05C8))  # огласовки и кантилляция

# Маппинг букв иврита → кириллица
LETTER_TO_CYR = {
    'א': 'ʼ', 'ב': 'б', 'ג': 'г', 'ד': 'д', 'ה': 'h',
    'ו': 'в', 'ז': 'з', 'ח': 'х', 'ט': 'т', 'י': 'й',
    'כ': 'к', 'ך': 'к', 'ל': 'л', 'מ': 'м', 'ם': 'м',
    'נ': 'н', 'ן': 'н', 'ס': 'с', 'ע': 'ʻ',
    'פ': 'п', 'ף': 'п', 'צ': 'ц', 'ץ': 'ц', 'ק': 'к',
    'ר': 'р', 'ש': 'ш', 'ת': 'т',
}

# Маппинг огласовок → гласные кириллицы
NIQQUD_TO_VOWEL = {
    '\u05B0': '',    # шва — в середине слова пропускаем
    '\u05B1': 'э',   # хатаф-сегол
    '\u05B2': 'а',   # хатаф-патах
    '\u05B3': 'о',   # хатаф-камац
    '\u05B4': 'и',   # хирик
    '\u05B5': 'э',   # цере
    '\u05B6': 'э',   # сегол
    '\u05B7': 'а',   # патах
    '\u05B8': 'а',   # камац
    '\u05B9': 'о',   # холам
    '\u05BB': 'у',   # куббуц
    '\u05BC': '',    # дагеш/маппик
    '\u05C1': 'с',   # шин-точка (син)
}

# Ключи строк для форматирования
LINE_KEYS = ['paleo', 'qumran', 'hebrew', 'lxx', 'translit', 'translation']
LINE_LABELS = ['палео-иврит', 'кумран', 'масоретский', 'lxx греческий', 'транслитерация', 'перевод']
LINE_COLORS = ['#d4a574', '#cd853f', '#e8e8e8', '#7ec8e3', '#888', '#e8e8e8']


# ═══════════════════════════════════════════════════════════════════
# ЗАГРУЗКА ДАННЫХ
# ═══════════════════════════════════════════════════════════════════

def load_json(path):
    if not path.exists():
        print(f"⚠ Файл не найден: {path}", file=sys.stderr)
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_verse_data(book, chapter, verse):
    """Получает данные стиха из translation.json, затем из кэша Sefaria."""
    # 1. Пробуем translation.json
    trans = load_json(TRANSLATION_PATH)
    if trans is not None:
        try:
            return trans[book][str(chapter)][str(verse)]
        except KeyError:
            pass

    # 2. Пробуем кэш Sefaria
    sefaria_data = get_verse_from_sefaria_cache(book, chapter, verse)
    if sefaria_data:
        return {
            "he": sefaria_data.get("hebrew", ""),
            "translation": sefaria_data.get("english", ""),
            "words": [
                {
                    "he": w,
                    "trans": transliterate_word(w),
                    "ru": ""
                } for w in sefaria_data.get("hebrew", "").split()
            ]
        }

    return None


def get_verse_from_sefaria_cache(book, chapter, verse):
    """Загружает стих из кэша Sefaria."""
    if not TANAKH_CACHE_DIR.exists():
        return None
    # Пробуем найти файл кэша
    cache_file = TANAKH_CACHE_DIR / book / f"{chapter}.json"
    if not cache_file.exists():
        return None
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        verses = data.get("verses", [])
        for v in verses:
            if v.get("verse") == verse:
                return v
    except Exception:
        pass
    return None


def get_qumran_for_verse(book, chapter, verse):
    """Получает кумранские разночтения для стиха."""
    q_data = load_json(QUMRAN_PATH)
    if q_data is None:
        return None
    try:
        return q_data[book][str(chapter)][str(verse)]
    except KeyError:
        return None


def get_lxx_for_verse(book, chapter, verse):
    """Получает текст Септуагинты для стиха."""
    lxx_data = load_json(LXX_PATH)
    if lxx_data is None:
        return None
    try:
        return lxx_data[book][str(chapter)][str(verse)]
    except KeyError:
        return None


# ═══════════════════════════════════════════════════════════════════
# ОБРАБОТКА ТЕКСТА
# ═══════════════════════════════════════════════════════════════════

def strip_niqqud(text):
    """Удаляет огласовки и кантилляцию из ивритского текста."""
    return ''.join(ch for ch in text if ord(ch) not in NIQQUD_MARKS)


def to_paleo(hebrew_text, paleo_map):
    """Конвертирует иврит (без огласовок) в палео-иврит."""
    clean = strip_niqqud(hebrew_text)
    result = []
    for ch in clean:
        if ch in paleo_map:
            result.append(paleo_map[ch])
        elif ch == ' ':
            result.append(' ')
        elif ch == '\u05BE':
            result.append('-')
        elif ord(ch) in HEBREW_LETTERS:
            result.append(ch)
        else:
            result.append(ch)
    return ''.join(result)


def parse_hebrew_clusters(hebrew_text):
    """Разбивает ивритский текст на кластеры: каждый согласный + огласовки."""
    clusters = []
    current_consonant = None
    current_niqqud = []

    for ch in hebrew_text:
        code = ord(ch)
        if code in HEBREW_LETTERS:
            if current_consonant is not None:
                clusters.append((current_consonant, ''.join(current_niqqud)))
            current_consonant = ch
            current_niqqud = []
        elif code in NIQQUD_MARKS and current_consonant is not None:
            current_niqqud.append(ch)
        else:
            if current_consonant is not None:
                clusters.append((current_consonant, ''.join(current_niqqud)))
                current_consonant = None
                current_niqqud = []
            clusters.append(ch)

    if current_consonant is not None:
        clusters.append((current_consonant, ''.join(current_niqqud)))

    return clusters


def transliterate_cluster(consonant, niqqud_str, is_first_in_word=True):
    """Транслитерирует один кластер (буква + огласовки) в кириллицу."""
    base = LETTER_TO_CYR.get(consonant, consonant)
    vowels = []
    has_shva = False
    for n in niqqud_str:
        if n == '\u05B0':
            has_shva = True
        elif n == '\u05BC':
            continue
        elif n in NIQQUD_TO_VOWEL:
            vowels.append(NIQQUD_TO_VOWEL[n])

    if consonant == 'ו' and '\u05BC' in niqqud_str:
        base = 'у'; vowels = []
    if consonant == 'ו' and '\u05B9' in niqqud_str:
        base = 'о'; vowels = []
    if '\u05B9' in niqqud_str and consonant != 'ו':
        if not vowels or vowels != ['о']:
            vowels = ['о']

    if not vowels and has_shva and not is_first_in_word:
        return base
    elif not vowels and has_shva and is_first_in_word:
        return base + 'э'
    elif not vowels:
        return base
    else:
        return base + ''.join(vowels)


def transliterate_word(hebrew_word):
    """Транслитерирует одно слово иврита в кириллицу."""
    clusters = parse_hebrew_clusters(hebrew_word)
    result = []
    word_start = True
    for c in clusters:
        if isinstance(c, str):
            if c == '\u05BE':
                result.append('-')
                word_start = True
                continue
            result.append(c)
            continue
        consonant, niqqud = c
        trans = transliterate_cluster(consonant, niqqud, is_first_in_word=word_start)
        result.append(trans)
        word_start = False
    return ''.join(result)


def split_greek_words(greek_text):
    """Разбивает греческий текст на слова."""
    return greek_text.split()


def distribute_lxx_words(lxx_words, num_columns):
    """Распределяет LXX-слова по колонкам MT (сглаживание разницы в количестве)."""
    if not lxx_words:
        return [''] * num_columns
    if len(lxx_words) == num_columns:
        return lxx_words
    if len(lxx_words) < num_columns:
        # Добавляем пустые колонки слева (греческий часто начинается с союза)
        result = [''] * (num_columns - len(lxx_words)) + lxx_words
        return result
    # Если слов больше — объединяем лишние
    merged = []
    ratio = len(lxx_words) / num_columns
    idx = 0.0
    for i in range(num_columns):
        end = int(round(idx + ratio))
        if i == num_columns - 1:
            end = len(lxx_words)
        merged.append(' '.join(lxx_words[int(idx):end]))
        idx = end
    return merged


# ═══════════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ КОЛОНОК
# ═══════════════════════════════════════════════════════════════════

def generate_six_lines(book, chapter, verse, paleo_map, use_data=True):
    """
    Генерирует 6 строк для одного стиха.
    Возвращает словарь с колонками и метаданными.
    """
    # 1. MT (масоретский)
    mt_data = None
    if use_data:
        mt_data = get_verse_data(book, chapter, verse)

    if mt_data and 'words' in mt_data and mt_data['words']:
        mt_words = mt_data['words']
        hebrew_base = [w['he'] for w in mt_words]
        translit_base = [w.get('trans', transliterate_word(w['he'])) for w in mt_words]
        trans_base = [w.get('ru', '') for w in mt_words]
    else:
        hebrew_text = mt_data['he'] if mt_data else f"[{book} {chapter}:{verse} не найден]"
        hebrew_base = hebrew_text.split()
        translit_base = [transliterate_word(w) for w in hebrew_base]
        trans_base = []

    num_cols = len(hebrew_base)

    # 2. Палео-иврит
    paleo_base = [to_paleo(w, paleo_map) for w in hebrew_base]

    # 3. Кумран
    qumran_data = get_qumran_for_verse(book, chapter, verse)
    qumran_base = [''] * num_cols
    qumran_info = ''
    if qumran_data and 'variants' in qumran_data:
        for variant in qumran_data['variants']:
            r = variant.get('reading', '')
            src = variant.get('source', '')
            notes = variant.get('notes', '')
            if r:
                mt = variant.get('masoretic', '')
                qumran_info = f"[{src}: {notes}]"
                mt_clean = strip_niqqud(mt) if mt else ''
                found = False
                for i, w in enumerate(hebrew_base):
                    w_clean = strip_niqqud(w)
                    # Сравниваем без огласовок: ищем mt_clean внутри w_clean
                    if mt_clean and mt_clean in w_clean:
                        qumran_base[i] = r
                        found = True
                        break
                    # Также проверяем: если mt_clean — это часть w_clean (например, יִשְׂרָאֵל внутри בְּנֵי יִשְׂרָאֵל)
                    mt_parts = mt_clean.split()
                    for mp in mt_parts:
                        if mp and mp in w_clean:
                            qumran_base[i] = r
                            found = True
                            break
                    if found:
                        break
                if not found and qumran_base:
                    # Ставим в последнюю непустую колонку
                    for i in range(num_cols - 1, -1, -1):
                        if hebrew_base[i].strip():
                            qumran_base[i] = r
                            break
    has_qumran = any(bool(x) for x in qumran_base) or bool(qumran_info)

    # 4. LXX (греческий)
    lxx_data = get_lxx_for_verse(book, chapter, verse)
    lxx_base = [''] * num_cols
    if lxx_data and 'words' in lxx_data:
        lxx_words = [w['grc'] for w in lxx_data['words']]
        lxx_base = distribute_lxx_words(lxx_words, num_cols)
    elif lxx_data:
        lxx_text = lxx_data.get('he', '')
        if lxx_text:
            words = lxx_text.split()
            lxx_base = distribute_lxx_words(words, num_cols)

    # Собираем колонки
    columns = []
    for i in range(num_cols):
        columns.append({
            'paleo': paleo_base[i] if i < len(paleo_base) else '',
            'qumran': qumran_base[i] if i < len(qumran_base) else '',
            'hebrew': hebrew_base[i] if i < len(hebrew_base) else '',
            'lxx': lxx_base[i] if i < len(lxx_base) else '',
            'translit': translit_base[i] if i < len(translit_base) else '',
            'translation': trans_base[i] if i < len(trans_base) else '',
        })

    return {
        'columns': columns,
        'num_cols': num_cols,
        'has_qumran': has_qumran,
        'qumran_info': qumran_info,
        'has_lxx': bool(lxx_base and any(lxx_base)),
    }


def compute_col_widths(columns):
    """Вычисляет ширину каждой колонки по самому длинному слову во всех строках."""
    widths = []
    for c in columns:
        w = max(
            len(c.get('paleo', '')),
            len(c.get('qumran', '')),
            len(c.get('hebrew', '')),
            len(c.get('lxx', '')),
            len(c.get('translit', '')),
            len(c.get('translation', '')),
            1
        )
        widths.append(w + 2)
    return widths


def pad_word(word, width):
    """Дополняет слово пробелами слева-направо до указанной ширины."""
    word = word if word else ''
    return word.ljust(width)


def build_row(words, widths):
    """Собирает строку из слов с фиксированной шириной колонок."""
    return ''.join(pad_word(w, widths[i]) for i, w in enumerate(words))


# ═══════════════════════════════════════════════════════════════════
# ФОРМАТИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════════

def format_html_terminal(verses_data, book_name, chapter_num):
    """Форматирует подстрочник в HTML (6 строк, терминальный стиль)."""
    dt = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        '<!DOCTYPE html>',
        '<html lang="ru">',
        '<head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'<title>Подстрочник — {book_name} {chapter_num}</title>',
        '<style>',
        '  * { margin: 0; padding: 0; box-sizing: border-box; }',
        '  body { background: #ede0c8; color: #2c1810; font-family: "Courier New", "Consolas", "Fira Code", monospace; font-size: 14px; line-height: 1.5; padding: 32px 16px; }',
        '  .container { max-width: 1200px; margin: 0 auto; }',
        '  h1 { color: #b8860b; font-size: 15px; font-weight: 400; letter-spacing: 1px; text-transform: uppercase; border-bottom: 1px solid #d4c4a8; padding-bottom: 12px; margin-bottom: 8px; }',
        '  .subtitle { color: #8a7a6a; font-size: 11px; margin-bottom: 28px; letter-spacing: 0.5px; }',
        '  .verse { margin-bottom: 20px; }',
        '  .verse-header { color: #b8860b; font-size: 11px; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; opacity: 0.6; }',
        '  .line-paleo { color: #b8860b; white-space: pre; }',
        '  .line-qumran { color: #8a7a6a; white-space: pre; }',
        '  .line-hebrew { color: #2c1810; white-space: pre; }',
        '  .line-lxx { color: #8a7a6a; white-space: pre; }',
        '  .line-translit { color: #8a7a6a; white-space: pre; }',
        '  .line-translation { color: #2c1810; white-space: pre; }',
        '  .qumran-note { color: #8a7a6a; font-size: 11px; margin: 2px 0 4px 0; font-style: italic; }',
        '  .sep { height: 1px; background: #d4c4a8; margin: 0 0 16px 0; }',
        '  footer { margin-top: 40px; padding-top: 12px; border-top: 1px solid #d4c4a8; color: #8a7a6a; font-size: 11px; }',
        '  @media (max-width: 768px) { body { font-size: 11px; padding: 16px 8px; } }',
        '</style>',
        '</head>',
        '<body>',
        '<div class="container">',
        f'<h1>◈ {book_name} {chapter_num}  ·  подстрочник</h1>',
        '<div class="subtitle">палео-иврит  /  кумран  /  масоретский  /  lxx  /  транслитерация  /  перевод</div>',
    ]

    for v in verses_data:
        cols = v['column_data']
        widths = v['col_widths']
        has_q = v.get('has_qumran', False)
        qi = v.get('qumran_info', '')
        has_lxx = v.get('has_lxx', False)

        lines.append('<div class="verse">')
        lines.append(f'<div class="verse-header">стих {v["verse"]}</div>')

        # Строка 1: палео-иврит
        lines.append(f'<div class="line-paleo">{build_row([c["paleo"] for c in cols], widths)}</div>')
        # Строка 2: кумран (если есть)
        q_words = [c['qumran'] for c in cols]
        if has_q:
            lines.append(f'<div class="line-qumran">{build_row(q_words, widths)}</div>')
        # Строка 3: масоретский
        lines.append(f'<div class="line-hebrew">{build_row([c["hebrew"] for c in cols], widths)}</div>')
        # Строка 4: LXX греческий (если есть)
        lxx_words = [c['lxx'] for c in cols]
        if has_lxx:
            lines.append(f'<div class="line-lxx">{build_row(lxx_words, widths)}</div>')
        # Строка 5: транслитерация
        lines.append(f'<div class="line-translit">{build_row([c["translit"] for c in cols], widths)}</div>')
        # Строка 6: перевод
        lines.append(f'<div class="line-translation">{build_row([c["translation"] for c in cols], widths)}</div>')
        # Примечание о кумранском разночтении
        if has_q and qi:
            lines.append(f'<div class="qumran-note">{qi}</div>')

        lines.append('</div>')

    lines.append(f'<footer>сгенерировано tools/interlinear-generator.py · {dt}</footer>')
    lines.append('</div>')
    lines.append('</body>')
    lines.append('</html>')
    return '\n'.join(lines)


def format_text_word_columns(verses_data, book_name, chapter_num):
    """Форматирует подстрочник как 6 строк с выравниванием по колонкам."""
    lines = [
        f'{book_name} {chapter_num} — Подстрочник',
        f'{"=" * 80}',
        '',
    ]

    for v in verses_data:
        cols = v['column_data']
        widths = v['col_widths']
        has_q = v.get('has_qumran', False)
        qi = v.get('qumran_info', '')
        has_lxx = v.get('has_lxx', False)

        lines.append(f'Стих {v["verse"]}:')

        lines.append('  ' + build_row([c['paleo'] for c in cols], widths))
        if has_q:
            lines.append('  ' + build_row([c['qumran'] for c in cols], widths))
        lines.append('  ' + build_row([c['hebrew'] for c in cols], widths))
        if has_lxx:
            lines.append('  ' + build_row([c['lxx'] for c in cols], widths))
        lines.append('  ' + build_row([c['translit'] for c in cols], widths))
        lines.append('  ' + build_row([c['translation'] for c in cols], widths))
        if has_q and qi:
            lines.append(f'  ─ {qi}')
        lines.append('')

    return '\n'.join(lines)


def format_markdown_word_columns(verses_data, book_name, chapter_num):
    """Форматирует подстрочник в Markdown (6 строк)."""
    lines = [
        f'# 📖 {book_name} {chapter_num} — Подстрочник',
        '',
    ]

    for v in verses_data:
        cols = v['column_data']
        widths = v['col_widths']
        has_q = v.get('has_qumran', False)
        qi = v.get('qumran_info', '')
        has_lxx = v.get('has_lxx', False)

        lines.append(f'## Стих {v["verse"]}')
        lines.append('')

        # Markdown-таблица со всеми строками
        n = len(cols)
        lines.append(f'| **Палео-иврит** | {" | ".join(c["paleo"] for c in cols)} |')
        if has_q:
            lines.append(f'| **Кумран** | {" | ".join(c["qumran"] for c in cols)} |')
        lines.append(f'| **Масоретский** | {" | ".join(c["hebrew"] for c in cols)} |')
        if has_lxx:
            lines.append(f'| **LXX** | {" | ".join(c["lxx"] for c in cols)} |')
        lines.append(f'| **Транслитерация** | {" | ".join(c["translit"] for c in cols)} |')
        lines.append(f'| **Перевод** | {" | ".join(c["translation"] for c in cols)} |')
        if has_q and qi:
            lines.append('')
            lines.append(f'*{qi}*')
        lines.append('')
        lines.append('---')
        lines.append('')

    lines.append(f'*Сгенерировано tools/interlinear-generator.py, {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M")}*')
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════
# ПАРСИНГ ССЫЛКИ
# ═══════════════════════════════════════════════════════════════════

def parse_ref(ref_str):
    match = re.match(r'^(\S+)\s+(\d+):(\d+)(?:-(\d+))?$', ref_str)
    if not match:
        raise ValueError(f"Неверный формат ссылки: {ref_str!r}")
    book = match.group(1)
    chapter = int(match.group(2))
    start_verse = int(match.group(3))
    end_verse = int(match.group(4)) if match.group(4) else start_verse
    if end_verse < start_verse:
        raise ValueError(f"Начальный стих > конечного")
    return book, chapter, list(range(start_verse, end_verse + 1))


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Генератор подстрочника ТаНаХа (6 строк: палео, кумран, MT, LXX, транслит, перевод)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python tools/interlinear-generator.py "bereshit 1:1-5" --output test-interlinear.html
  python tools/interlinear-generator.py "dvarim 32:8" --format text
  python tools/interlinear-generator.py "bereshit 1:1" --format md
        """
    )
    parser.add_argument('ref', type=str, nargs='?',
                        help='Ссылка "book chapter:verse" или "book chapter:start-end"')
    parser.add_argument('--book', '-b', help='Название книги')
    parser.add_argument('--chapter', '-c', type=int, help='Номер главы')
    parser.add_argument('--verse', '-v', type=str, help='Номер стиха или диапазон')
    parser.add_argument('--format', '-f', choices=['html', 'md', 'text'], default='html',
                        help='Формат вывода (по умолчанию: html)')
    parser.add_argument('--output', '-o', type=str, default=None, help='Файл для сохранения')
    parser.add_argument('--no-data', action='store_true',
                        help='Не использовать translation.json')

    args = parser.parse_args()

    ref_str = args.ref
    if not ref_str and args.book and args.chapter and args.verse:
        ref_str = f"{args.book} {args.chapter}:{args.verse}"
    if not ref_str:
        parser.print_help()
        print("\nОшибка: укажите ссылку на стих(и).", file=sys.stderr)
        sys.exit(1)

    try:
        book, chapter, verses = parse_ref(ref_str)
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    paleo_map = load_json(PALEO_MAP_PATH)
    if paleo_map is None:
        print("⚠ Палео-карта не найдена", file=sys.stderr)
        paleo_map = {}

    # Имя книги
    book_name = book.capitalize()
    try:
        module_path = BASE_DIR / "tools" / "generators" / "generate-tanakh-content.py"
        if module_path.exists():
            spec = importlib.util.spec_from_file_location("generate_tanakh_content", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            BOOKS_DATA = getattr(module, 'BOOKS_DATA', {})
            book_info = BOOKS_DATA.get(book, {})
            book_name = book_info.get('ru', book.capitalize())
    except Exception as e:
        print(f"⚠ {e}", file=sys.stderr)

    # Генерация
    use_data = not args.no_data
    verses_data = []
    for v in verses:
        result = generate_six_lines(book, chapter, v, paleo_map, use_data=use_data)
        cols = result['columns']
        widths = compute_col_widths(cols)
        verses_data.append({
            'verse': v,
            'columns': cols,
            'column_data': cols,
            'col_widths': widths,
            'has_qumran': result['has_qumran'],
            'qumran_info': result['qumran_info'],
            'has_lxx': result['has_lxx'],
        })

    # Форматирование
    if args.format == 'html':
        output = format_html_terminal(verses_data, book_name, chapter)
    elif args.format == 'md':
        output = format_markdown_word_columns(verses_data, book_name, chapter)
    else:
        output = format_text_word_columns(verses_data, book_name, chapter)

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✅ Подстрочник сохранён в {output_path}")
    else:
        print(output)


if __name__ == '__main__':
    main()