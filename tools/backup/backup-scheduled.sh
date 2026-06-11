#!/bin/bash
# create-backup-scheduled.sh — автоматический бэкап репозитория (для cron)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."
BACKUP_DIR="$REPO_ROOT/../golem-backups"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/golem-$DATE.tar.gz"
LOG_FILE="$BACKUP_DIR/backup.log"

mkdir -p "$BACKUP_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "Начало бэкапа"

cd "$REPO_ROOT" || exit 1

tar -czf "$BACKUP_FILE" \
    --exclude=".git" \
    --exclude="export.txt" \
    --exclude="structure.txt" \
    --exclude="golem-backups" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    .

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "✅ Бэкап создан: $BACKUP_FILE (размер: $SIZE)"
    
    cd "$BACKUP_DIR" || exit 1
    ls -t | tail -n +11 | xargs -r rm
    log "🧹 Очищено: оставлено 10 последних бэкапов"
else
    log "❌ Ошибка создания бэкапа"
    exit 1
fi

log "Завершено"
