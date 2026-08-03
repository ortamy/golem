#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Читает иврит из xlsx и заполняет hebrew/paleo в bereshit-1.json."""
import json, zipfile, xml.etree.ElementTree as ET, re, sys

XLSX = 'archive/Original-Hebrew-Bible-Spreadsheet-Version-1.0.xlsx'
JSON_PATH = 'products/website/apps/researchlab/data/scripture/bereshit-1.json'
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

# Иврит → Палео (из paleo-letters.js)
HE_TO_PALEO = {
    'א':'𐤀','ב':'𐤁','ג':'𐤂','ד':'𐤃','ה':'𐤄','ו':'𐤅','ז':'𐤆',
    'ח':'𐤇','ט':'𐤈','י':'𐤉','כ':'𐤊','ך':'𐤊','ל':'𐤋','מ':'𐤌',
    'ם':'𐤌','נ':'𐤍','ן':'𐤍','ס':'𐤎','ע':'𐤏','פ':'𐤐','ף':'𐤐',
    'צ':'𐤑','ץ':'𐤑','ק':'𐤒','ר':'𐤓','ש':'𐤔','ת':'𐤕',
}

def to_paleo(hebrew):
    return ''.join(HE_TO_PALEO.get(c, c) for c in hebrew)

def read_xlsx(path):
    """Читает xlsx без внешних библиотек. Возвращает список строк."""
    try:
        z = zipfile.ZipFile(path)
    except Exception as e:
        print(f'Не удалось открыть xlsx: {e}')
        return None
    # Читаем shared strings
    strings = []
    try:
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root.findall(f'{NS}si'):
            text = ''.join(t.text or '' for t in si.iter(f'{NS}t'))
            strings.append(text)
    except Exception:
        pass
    # Читаем первый лист
    rows = []
    try:
        root = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        for row in root.iter(f'{NS}row'):
            cells = []
            for c in row.findall(f'{NS}c'):
                t = c.get('t', 's')
                v = c.find(f'{NS}v')
                val = v.text if v is not None else ''
                if t == 's' and val.isdigit():
                    val = strings[int(val)] if int(val) < len(strings) else ''
                cells.append(val)
            rows.append(cells)
    except Exception as e:
        print(f'Не удалось прочитать лист: {e}')
        return None
    return rows

def main():
    rows = read_xlsx(XLSX)
    if not rows:
        print('xlsx не читается. Нужен источник ивритского текста.')
        sys.exit(1)
    # Ищем колонку с ивритом (содержит буквы иврита)
    hebrew_col = None
    for r, row in enumerate(rows[:5]):
        for c, val in enumerate(row):
            if val and re.search(r'[\u0590-\u05ff]', val):
                hebrew_col = c
                print(f'Найдена колонка иврита: {c} (строка {r})')
                break
        if hebrew_col is not None:
            break
    if hebrew_col is None:
        print('Колонка с ивритом не найдена в xlsx.')
        # Показываем первые 3 строки для диагностики
        for r in rows[:3]:
            print('  ', r[:5])
        sys.exit(1)
    # Собираем ивритские тексты
    hebrew_texts = []
    for row in rows[1:]:  # пропускаем заголовок
        val = row[hebrew_col] if hebrew_col < len(row) else ''
        if val and re.search(r'[\u0590-\u05ff]', val):
            hebrew_texts.append(val.strip())
    print(f'Найдено ивритских текстов: {len(hebrew_texts)}')
    # Загружаем JSON
    with open(JSON_PATH, encoding='utf-8') as f:
        verses = json.load(f)
    # Заполняем
    updated = 0
    for i, verse in enumerate(verses):
        if verse.get('hebrew') and verse['hebrew'].strip():
            continue  # уже заполнен
        if i < len(hebrew_texts):
            hebrew = hebrew_texts[i]
            verse['hebrew'] = hebrew
            verse['paleo'] = to_paleo(re.sub(r'[\u0591-\u05C7]', '', hebrew))
            # Обновляем words[]
            words = verse.get('words', [])
            hebrew_words = hebrew.split()
            paleo_words = verse['paleo'].split()
            for j, w in enumerate(words):
                if j < len(hebrew_words):
                    w['hebrew'] = hebrew_words[j]
                if j < len(paleo_words):
                    w['paleo'] = paleo_words[j]
            updated += 1
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(verses, f, ensure_ascii=False, indent=2)
    print(f'Обновлено стихов: {updated} из {len(verses)}')

if __name__ == '__main__':
    main()