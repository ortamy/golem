#!/usr/bin/env python3
"""Debug script: check what arrows and ellipsis look like in files."""
import re, os

files = [
    'content/researches/systems/bavel-sacrifice.md',
    'content/researches/media/disney-epstein.md',
    'content/researches/systems/talmud-judaism.md',
    'content/researches/history/enuma-exposed.md',
]

for fp in files:
    if not os.path.exists(fp):
        print(f"[SKIP] {fp}")
        continue
    with open(fp, encoding='utf-8') as f:
        content = f.read()
    
    total_arrows = len(re.findall(r'\u2192', content))
    total_ellipsis = len(re.findall(r'\.\.\.', content))
    
    print(f"\n{'='*60}")
    print(f"FILE: {fp}")
    print(f"Total arrows: {total_arrows}")
    print(f"Total ellipsis: {total_ellipsis}")
    
    # Find lines with arrows (first 10)
    print(f"\n--- First 10 lines with \u2192 ---")
    count = 0
    for i, line in enumerate(content.split('\n')):
        if '\u2192' in line:
            print(f"  L{i+1}: {line.strip()[:150]}")
            count += 1
            if count >= 10:
                break
    
    # Find lines with ellipsis (first 10)
    print(f"\n--- First 10 lines with ... ---")
    count = 0
    for i, line in enumerate(content.split('\n')):
        if '...' in line:
            print(f"  L{i+1}: {line.strip()[:150]}")
            count += 1
            if count >= 10:
                break

    # Check if arrows are part of glossary pattern: word → WORD — description
    arrow_contexts = re.findall(r'([^\n]*?\u2192[^\n]*)', content)
    regular_arrows = 0
    for ctx in arrow_contexts:
        if re.match(r'.*?[а-яА-Яa-zA-Z]+\s*\u2192\s*[А-ЯA-Z].*', ctx):
            regular_arrows += 1
    
    print(f"\nArrows in glossary-like pattern: {regular_arrows} / {total_arrows}")