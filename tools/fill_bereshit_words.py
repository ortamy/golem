#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерирует words[] для всех стихов Берешит из translit и literal."""
import json

PATH = 'products/website/apps/researchlab/data/scripture/bereshit-1.json'

with open(PATH, encoding='utf-8') as f:
    verses = json.load(f)

updated = 0
for verse in verses:
    # Пропускаем стихи, где words уже заполнены (например, 1:1).
    if verse.get('words') and len(verse['words']) > 0:
        continue

    translit = verse.get('translit', '')
    literal = verse.get('literal', '')
    hebrew = verse.get('hebrew', '')
    paleo = verse.get('paleo', '')

    # Разбиваем на слова.
    translit_words = translit.split() if translit else []
    literal_words = literal.split() if literal else []
    hebrew_words = hebrew.split() if hebrew else []
    paleo_words = paleo.split() if paleo else []

    # Количество слов — по максимальному из доступных.
    count = max(len(translit_words), len(literal_words), len(hebrew_words), len(paleo_words), 1)

    words = []
    for i in range(count):
        words.append({
            'hebrew': hebrew_words[i] if i < len(hebrew_words) else '',
            'paleo': paleo_words[i] if i < len(paleo_words) else '',
            'translit': translit_words[i] if i < len(translit_words) else '',
            'literal': literal_words[i] if i < len(literal_words) else ''
        })

    verse['words'] = words
    updated += 1

with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(verses, f, ensure_ascii=False, indent=2)

print(f'Обновлено стихов: {updated} из {len(verses)}')