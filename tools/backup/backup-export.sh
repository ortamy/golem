#!/bin/bash
# tools/backup/backup-export.sh — backup export.sh
# export-repo.sh — выгружает все md-файлы в один текст

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."
OUTPUT="$REPO_ROOT/export.txt"

echo "📁 ВЫГРУЗКА РЕПОЗИТОРИЯ"
echo "========================"

# Очищаем выходной файл
> "$OUTPUT"

# Находим все .md файлы, сортируем, обрабатываем
find "$REPO_ROOT" -name "*.md" -type f | sort | while read -r file; do
    # Пропускаем export.txt и structure.txt
    if [[ "$file" == *"export.txt"* ]] || [[ "$file" == *"structure.txt"* ]]; then
        continue
    fi
    
    rel_path="${file#$REPO_ROOT/}"
    echo "=== $rel_path ===" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    cat "$file" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    echo "---" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
done

echo "✅ Готово: $OUTPUT"
echo "📊 Объём: $(wc -l < "$OUTPUT") строк"
echo "📁 Размер: $(du -h "$OUTPUT" | cut -f1)"
