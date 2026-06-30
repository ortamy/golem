#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f boot.bin ]; then
    echo "boot.bin not found. Run 'make' first."
    exit 1
fi

qemu-system-i386 -drive format=raw,file=boot.bin