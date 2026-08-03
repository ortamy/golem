#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка исследований на пустой/незаполненный контент."""
import json
import sys

PATH = 'products/website/apps/researchlab/data/exposures/index.json'

def is_empty_section(section):
    """Секция пуста, если нет body/heading или body пустой."""
    if not section:
        return True
    body = section.get('body') or section.get('content') or ''
    heading = section.get('heading') or section.get('title') or ''
    return not str(body).strip() and not str(heading).strip()

def analyze():
    with open(PATH, encoding='utf-8') as f:
        items = json.load(f)

    empty_items = []
    partial_items = []

    for item in items:
        title = item.get('title', 'Без названия')
        slug = item.get('slug', '')
        sections = item.get('sections') or {}
        content = sections.get('content') or []
        thesis = sections.get('thesis') or ''
        shift = sections.get('shift') or ''
        summary = item.get('summary') or ''

        # Полностью пустое: нет контента, нет тезиса, нет сдвига
        has_content = any(
            (sec.get('body') or sec.get('content') or '').strip()
            for sec in content
        )
        has_thesis = bool(str(thesis).strip())
        has_shift = bool(str(shift).strip())

        if not has_content and not has_thesis and not has_shift:
            empty_items.append({
                'title': title,
                'slug': slug,
                'summary': summary,
                'reason': 'Нет контента, тезиса и сдвига'
            })
        elif not has_content and (has_thesis or has_shift):
            partial_items.append({
                'title': title,
                'slug': slug,
                'summary': summary,
                'reason': 'Есть тезис/сдвиг, но нет секций content'
            })
        elif has_content:
            # Проверяем, есть ли секции с пустым body
            empty_sections = [
                sec.get('heading', 'Без заголовка')
                for sec in content
                if not (sec.get('body') or sec.get('content') or '').strip()
            ]
            if empty_sections:
                partial_items.append({
                    'title': title,
                    'slug': slug,
                    'summary': summary,
                    'reason': 'Пустые секции: ' + ', '.join(empty_sections[:5])
                })

    print('=' * 70)
    print('ВСЕГО ИССЛЕДОВАНИЙ:', len(items))
    print('=' * 70)

    print('\n--- ПОЛНОСТЬЮ ПУСТЫЕ (нет контента, тезиса, сдвига):', len(empty_items), '---')
    for i, item in enumerate(empty_items, 1):
        print(f'{i}. {item["title"]} (slug: {item["slug"]})')
        print(f'   Причина: {item["reason"]}')

    print('\n--- ЧАСТИЧНО ЗАПОЛНЕННЫЕ (есть тезис/сдвиг, но нет секций ИЛИ есть пустые секции):', len(partial_items), '---')
    for i, item in enumerate(partial_items, 1):
        print(f'{i}. {item["title"]} (slug: {item["slug"]})')
        print(f'   Причина: {item["reason"]}')

    print('\n' + '=' * 70)
    print('ИТОГО ПРОБЛЕМНЫХ:', len(empty_items) + len(partial_items))
    print('=' * 70)

if __name__ == '__main__':
    analyze()