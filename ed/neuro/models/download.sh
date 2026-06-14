#!/bin/bash
# ed/neuro/models/download.sh — download.sh
# download.sh — скачивание готовой модели ed-v1.gguf

set -e

MODEL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_PATH="$MODEL_DIR/ed-v1.gguf"

echo "📥 СКАЧИВАНИЕ МОДЕЛИ ЭД — СВИДЕТЕЛЬ"
echo "===================================="
echo ""

# Вариант 1: с Hugging Face (если модель выложена)
HF_REPO="golem/ed-v1"
HF_FILE="ed-v1-q4_k_m.gguf"

if command -v huggingface-cli &> /dev/null; then
    echo "Скачивание с Hugging Face: $HF_REPO/$HF_FILE"
    huggingface-cli download "$HF_REPO" "$HF_FILE" --local-dir "$MODEL_DIR"
    mv "$MODEL_DIR/$HF_FILE" "$OUTPUT_PATH"
    echo "✅ Модель скачана: $OUTPUT_PATH"
    exit 0
fi

# Вариант 2: прямая ссылка (если есть)
URL="https://example.com/models/ed-v1.gguf"

if command -v wget &> /dev/null; then
    echo "Скачивание по ссылке: $URL"
    wget -O "$OUTPUT_PATH" "$URL"
    echo "✅ Модель скачана: $OUTPUT_PATH"
    exit 0
fi

if command -v curl &> /dev/null; then
    echo "Скачивание по ссылке: $URL"
    curl -L -o "$OUTPUT_PATH" "$URL"
    echo "✅ Модель скачана: $OUTPUT_PATH"
    exit 0
fi

echo "❌ Не удалось скачать модель"
echo "   Установите huggingface-cli: pip install huggingface-hub"
echo "   или скачайте вручную и поместите в $OUTPUT_PATH"
exit 1
