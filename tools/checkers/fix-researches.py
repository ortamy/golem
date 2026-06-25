#!/usr/bin/env python3
"""
Safe fixer for research files. Only applies safe automatic fixes:
1. Adds missing "Файл" field to metadata block
2. Adds stub sections for missing required sections

Usage:
  python fix-researches.py --dry-run    # Preview only
  python fix-researches.py              # Apply changes
  python fix-researches.py --file content/researches/media/disney-epstein.md
"""

import os
import re
import sys

RESEARCHES_DIR = 'content/researches'
EXCLUDE_DIRS = {'archive', 'node_modules', '.git', '__pycache__'}

REQUIRED_SECTIONS = [
    ("ВВЕДЕНИЕ", "## 🔥 ВВЕДЕНИЕ\n\nTODO: написать введение\n"),
    ("РАЗОБЛАЧЕНИЕ", "## ⚔️ РАЗОБЛАЧЕНИЕ\n\nTODO: написать разоблачение\n"),
    ("СВОДКА", "## 📊 СВОДКА\n\nTODO: написать сводку\n"),
]


def fix_metadata_file_field(content, rel_path):
    """Add Файл field if missing."""
    # Check both formats
    has_file = bool(
        re.search(r'\*\*Файл\*\*:', content) or 
        re.search(r'\*\*Файл:\*\*', content)
    )
    if has_file:
        return content, None

    # Find metadata block start
    meta_start = re.search(r'\*\*Метаданные файла\*\*', content)
    if not meta_start:
        return content, None  # Can't find metadata block

    # Insert after the metadata header line
    end_of_line = content.index('\n', meta_start.end())
    insert_pos = end_of_line + 1
    
    file_path = f'`researches/{rel_path.replace(chr(92), "/")}`'
    field_line = f'- **Файл:** {file_path}\n'
    
    new_content = content[:insert_pos] + '\n' + field_line + content[insert_pos:]
    return new_content, f"added Файл: {file_path}"


def fix_missing_sections(content):
    """Add stub sections for missing required sections."""
    changes = []
    for section_name, section_template in REQUIRED_SECTIONS:
        has = bool(re.search(rf'##\s.*{re.escape(section_name)}', content))
        if has:
            continue
        
        # Find last --- to insert before it, or append to end
        last_hr = content.rfind('\n---\n')
        # But don't insert after the metadata block — find the real content end
        # Look for the last meaningful separator
        candidates = []
        for m in re.finditer(r'\n---\n', content):
            # Skip if this is within first 30 lines (metadata area)
            line_num = content[:m.start()].count('\n')
            if line_num > 25:
                candidates.append(m.start())
        
        if candidates:
            insert_pos = candidates[-1]
            content = (content[:insert_pos] + '\n\n' + section_template + 
                      '\n---\n' + content[insert_pos + 5:])
        else:
            content += '\n\n' + section_template + '\n'
        
        changes.append(f"added section {section_name}")
    
    return content, changes if changes else None


def fix_file(filepath, rel_path, dry_run=True):
    """Fix one file. Returns list of changes or None."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f"ERROR: {e}"]

    changes = []

    # 1. Add Файл field
    new_content, change = fix_metadata_file_field(content, rel_path)
    if change:
        changes.append(change)
        content = new_content

    # 2. Add missing sections
    new_content, section_changes = fix_missing_sections(content)
    if section_changes:
        changes.extend(section_changes)
        content = new_content

    if not changes:
        return None

    if dry_run:
        return changes

    # Write
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return changes


def find_md_files(root_dir):
    md_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith('.')]
        for fn in filenames:
            if fn.endswith('.md'):
                rel = os.path.relpath(os.path.join(dirpath, fn), root_dir)
                md_files.append((rel, os.path.join(dirpath, fn)))
    return sorted(md_files)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Safe fixer for research files')
    parser.add_argument('--dry-run', action='store_true', help='Preview only')
    parser.add_argument('--file', '-f', type=str, help='Fix specific file')
    args = parser.parse_args()

    mode = "DRY RUN" if args.dry_run else "APPLY"
    print(f"\n{'='*70}")
    print(f"  RESEARCH FILES FIXER - {mode}")
    print(f"{'='*70}")

    if args.file:
        fp = args.file if os.path.isabs(args.file) else os.path.join(RESEARCHES_DIR, args.file)
        if not os.path.exists(fp):
            print(f"  [X] Not found: {fp}")
            sys.exit(1)
        rel = os.path.relpath(fp, RESEARCHES_DIR)
        files = [(rel, fp)]
    else:
        files = find_md_files(RESEARCHES_DIR)

    total = 0
    fixed = 0
    unchanged = 0

    for rel, fp in files:
        changes = fix_file(fp, rel, args.dry_run)
        if changes is None:
            unchanged += 1
            continue
        fixed += 1
        total += len(changes)
        print(f"\n  [{'>' if args.dry_run else 'V'}] {rel}")
        for c in changes:
            print(f"      - {c}")

    print(f"\n{'='*70}")
    print(f"  Summary: {len(files)} files, {fixed} changed, {unchanged} unchanged")
    print(f"  Total changes: {total}")
    print(f"{'='*70}")
    if args.dry_run and total > 0:
        print(f"\n  To apply: python fix-researches.py")
    print()


if __name__ == '__main__':
    main()