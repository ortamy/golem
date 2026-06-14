import re
from pathlib import Path

root = Path('.')
count = 0
target_line_pattern = re.compile(r'> \*\*עֵד \(Эд\) — Свидетель\.\*\*')

for md_file in root.rglob('*.md'):
    if '.venv' in str(md_file):
        continue
    content = md_file.read_text(encoding='utf-8', errors='ignore')
    lines = content.splitlines(keepends=True)
    
    # Find the first line matching the target pattern
    found_idx = None
    for i, line in enumerate(lines):
        if target_line_pattern.match(line):
            found_idx = i
            break
    
    if found_idx is not None:
        # Keep only lines before the target line
        new_content = ''.join(lines[:found_idx])
        # Ensure file ends with a newline if it had content before
        if new_content and not new_content.endswith('\n'):
            new_content += '\n'
        md_file.write_text(new_content, encoding='utf-8')
        count += 1
        print(f'  ✅ {md_file} (removed {len(lines) - found_idx} lines)')

print(f'\nИзменено: {count} файлов')