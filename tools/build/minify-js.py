#!/usr/bin/env python3
"""
Minify JS files in products/website/js/ and products/website/app.js
Creates minified versions with .min.js extension, also generates source maps.

Usage:
    python3 tools/build/minify-js.py
    python3 tools/build/minify-js.py --no-source-maps

Options:
    --no-source-maps    Skip source map generation
    --check           Only check which files would be minified (dry run)
"""

import os
import re
import sys
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JS_DIR = os.path.join(BASE_DIR, 'products', 'website', 'js')
APP_JS = os.path.join(BASE_DIR, 'products', 'website', 'app.js')
OUTPUT_DIR = os.path.join(BASE_DIR, 'products', 'website')

def simple_minify(content):
    """Базовый минификатор JS: убирает комментарии, лишние пробелы, переносы строк."""
    # Убрать многострочные комментарии /* ... */
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    # Убрать однострочные комментарии // ... (но не в строках)
    lines = content.split('\n')
    result_lines = []
    for line in lines:
        # Простая обработка: убираем // вне строк
        in_string = False
        string_char = None
        clean_line = ''
        i = 0
        while i < len(line):
            ch = line[i]
            if in_string:
                clean_line += ch
                if ch == '\\' and i + 1 < len(line):
                    clean_line += line[i + 1]
                    i += 2
                    continue
                if ch == string_char:
                    in_string = False
            else:
                if ch in ('"', "'", '`'):
                    in_string = True
                    string_char = ch
                    clean_line += ch
                elif ch == '/' and i + 1 < len(line) and line[i + 1] == '/':
                    break  # skip rest of line
                else:
                    clean_line += ch
            i += 1
        result_lines.append(clean_line.rstrip())
    content = '\n'.join(result_lines)

    # Сжать пробелы
    content = re.sub(r'[ \t]+', ' ', content)
    # Убрать пробелы вокруг операторов
    content = re.sub(r'\s*([{}();,=+\-*/<>!&|?:])\s*', r'\1', content)
    # Убрать лишние пробелы в начале/конце строк
    lines = content.split('\n')
    lines = [line.strip() for line in lines]
    # Убрать пустые строки
    lines = [line for line in lines if line]
    content = ''.join(lines)  # Всё в одну строку (для JS это валидно)

    # Восстановить пробелы в некоторых конструкциях для безопасности
    content = re.sub(r'(var|let|const|return|if|else|for|while|function|typeof|instanceof|new|delete|void)\b', r'\1 ', content)
    content = re.sub(r'\b(case|catch|finally|switch|this|throw|try|in|of)\b', r'\1 ', content)

    return content


def generate_source_map(original_content, minified_content, filename):
    """Создаёт простую source map (VLQ-free) для отладки."""
    original_lines = original_content.split('\n')
    mappings = []
    for i, line in enumerate(minified_content.split('\n')):
        mappings.append(f'{i},0,{i},0,0')
    return {
        "version": 3,
        "file": filename,
        "sources": [filename.replace('.min.js', '.js')],
        "names": [],
        "mappings": ';'.join(mappings),
        "sourcesContent": [original_content]
    }


def process_file(filepath, dry_run=False, source_maps=True):
    """Minify single JS file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    if dry_run:
        original_size = len(original.encode('utf-8'))
        print(f'  {filepath}: {original_size} bytes')
        return True

    minified = simple_minify(original)
    minified_size = len(minified.encode('utf-8'))
    original_size = len(original.encode('utf-8'))
    savings = (1 - minified_size / original_size) * 100 if original_size else 0

    # Write minified file
    if filepath.endswith('.js'):
        min_path = filepath.replace('.js', '.min.js')
    else:
        min_path = filepath + '.min'

    with open(min_path, 'w', encoding='utf-8') as f:
        f.write(minified)

    print(f'  ✓ {filepath} → {min_path}')
    print(f'    Размер: {original_size} → {minified_size} bytes ({savings:.1f}% сжато)')

    # Write source map
    if source_maps:
        sm = generate_source_map(original, minified, os.path.basename(min_path))
        sm_path = min_path + '.map'
        import json
        with open(sm_path, 'w', encoding='utf-8') as f:
            json.dump(sm, f, ensure_ascii=False)
        print(f'    Source map: {sm_path}')

    return True


def main():
    dry_run = '--check' in sys.argv
    source_maps = '--no-source-maps' not in sys.argv

    if dry_run:
        print('Режим проверки (dry run):')
    else:
        print('Минификация JS файлов...')
        if source_maps:
            print('Source maps: включены')
        else:
            print('Source maps: отключены')

    all_ok = True

    # Minify all .js files in js/ directory
    if os.path.exists(JS_DIR):
        for root, dirs, files in os.walk(JS_DIR):
            for f in sorted(files):
                if f.endswith('.js') and not f.endswith('.min.js'):
                    filepath = os.path.join(root, f)
                    if not process_file(filepath, dry_run, source_maps):
                        all_ok = False

    # Minify app.js
    if os.path.exists(APP_JS):
        if not process_file(APP_JS, dry_run, source_maps):
            all_ok = False

    if dry_run:
        print(f'\nНайдено JS файлов для минификации.')
    else:
        print(f'\nГотово!')

    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())