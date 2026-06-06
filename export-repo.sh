#!/bin/bash

# export-repo.sh — выгружает все md-файлы в один текст

OUTPUT="repo-full-export.txt"

echo "📁 ВЫГРУЗКА РЕПОЗИТОРИЯ"
echo "========================"
echo ""

# Очищаем выходной файл
> "$OUTPUT"

# Находим все .md файлы, сортируем, обрабатываем
find . -name "*.md" -type f | sort | while read -r file; do
    echo "=== $file ===" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    cat "$file" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    echo "---" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
done

echo "✅ Готово: $OUTPUT"
echo "📊 Объём: $(wc -l < "$OUTPUT") строк"
echo "📁 Размер: $(du -h "$OUTPUT" | cut -f1)"
