#!/bin/bash
# tools/backup/backup-create.sh — backup create.sh
# backup.sh — бэкап репозитория

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."
BACKUP_DIR="$REPO_ROOT/../golem-backups"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/golem-$DATE.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "💾 БЭКАП РЕПОЗИТОРИЯ"
echo "===================="
echo "Источник: $REPO_ROOT"
echo "Назначение: $BACKUP_FILE"

# Создаём архив (исключая .git и backup-файлы)
tar -czf "$BACKUP_FILE" \
    --exclude="$REPO_ROOT/.git" \
    --exclude="$REPO_ROOT/export.txt" \
    --exclude="$REPO_ROOT/structure.txt" \
    --exclude="$BACKUP_DIR" \
    -C "$REPO_ROOT" .

echo ""
echo "✅ Бэкап создан: $BACKUP_FILE"
echo "📊 Размер: $(du -h "$BACKUP_FILE" | cut -f1)"

# Оставляем только 10 последних бэкапов
cd "$BACKUP_DIR"
ls -t | tail -n +11 | xargs -r rm
echo "🧹 Очищено: оставлено 10 последних бэкапов"
