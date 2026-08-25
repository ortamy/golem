#!/usr/bin/env python3
"""CLI-точка входа агентной системы."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
except ImportError:  # CLI работает и без установки необязательной загрузки .env.
    def load_dotenv(_path):
        return False
from orchestrator import dispatch

load_dotenv(ROOT / ".env")


def main():
    parser = argparse.ArgumentParser(description="Оркестратор пайплайнов Голема")
    parser.add_argument("query", nargs="+", help="Запрос на русском языке")
    args = parser.parse_args()
    result = dispatch(" ".join(args.query))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
