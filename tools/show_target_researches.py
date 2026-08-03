#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Показывает текущее состояние целевых исследований."""
import json

PATH = 'products/website/apps/researchlab/data/exposures/index.json'
TARGETS = [
    'archive-adrenokhrom',
    'archive-disney-i-epstein',
    'archive-twin-towers',
    'archive-bavel-layer',
]

with open(PATH, encoding='utf-8') as f:
    items = json.load(f)

for item in items:
    if item.get('slug') not in TARGETS:
        continue
    print('=' * 70)
    print('TITLE:', item['title'])
    print('SLUG:', item['slug'])
    s = item.get('sections', {})
    print('  thesis:', repr(s.get('thesis', ''))[:120])
    print('  shift:', repr(s.get('shift', ''))[:120])
    content = s.get('content', [])
    print('  content sections:', len(content))
    for n, sec in enumerate(content):
        body = sec.get('body') or sec.get('content') or ''
        status = 'EMPTY' if not str(body).strip() else 'ok'
        print(f'    [{n}] {status}: {sec.get("heading")!r}  body_len={len(str(body))}')