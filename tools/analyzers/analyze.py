#!/usr/bin/env python3
"""CLI вертикального анализатора слоёв подмен.

Метаданные файла:
- Заголовок: командный анализатор «Голем»
- Описание: форматированный терминальный запуск движка анализаторов
- Версия: 1.0.0
- Дата создания: 2026-08-02
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, Optional

try:
    from .engine import AnalysisResult, Analyzer
except ImportError:  # Позволяет запускать файл напрямую из корня проекта.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.analyzers.engine import AnalysisResult, Analyzer


RESET = "\033[0m"
ORANGE = "\033[38;5;208m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"


def _paint(value: str, color: str, enabled: bool) -> str:
    return f"{color}{value}{RESET}" if enabled else value


def _line(char: str = "─", width: int = 72) -> str:
    return char * width


def _format_report(result: AnalysisResult, color: bool = True) -> str:
    out = [_paint(_line("═"), ORANGE, color), _paint(" ГОЛЕМ / АНАЛИЗАТОРЫ / ВЕРТИКАЛЬНЫЙ ПРОХОД", ORANGE, color), _paint(_line("═"), ORANGE, color)]
    out.append(f"Слова: {len(result.words)} | Предложения: {len(result.sentences)}")
    out.append("")
    out.append(_paint("[1] ТОКЕНИЗАЦИЯ", CYAN, color))
    out.append(f"  Слова выделены: {len(result.words)}")
    out.append(f"  Предложения выделены: {len(result.sentences)}")
    out.append("")
    out.append(_paint("[2] ПРОХОД ПО СЛОЯМ ПОДМЕНЫ", CYAN, color))
    for number, layer in enumerate(result.layers, 1):
        out.append(_paint(f"  {number:02d}. {layer.name}", ORANGE, color))
        out.append(f"      Совпадений слов: {layer.hit_count} | Доля: {layer.percentage:.2f}%")
        if layer.markers:
            marker_text = ", ".join(f"{hit.term}={_paint(str(hit.count), GREEN, color)} ({', '.join(hit.examples)})" for hit in layer.markers)
            out.append(f"      Маркеры: {marker_text}")
        else:
            out.append(f"      {_paint('Маркеры не найдены', DIM, color)}")
    out.extend(["", _paint("[3] СВОДКА", CYAN, color), _line()])
    out.append("  Слой                              Слова       Процент")
    out.append("  " + _line("-", 58))
    for layer in sorted(result.layers, key=lambda item: item.percentage, reverse=True):
        out.append(f"  {layer.name:<32} {layer.hit_count:>5}       {layer.percentage:>7.2f}%")
    out.append(_line())
    if result.dominant_layer:
        dominant = result.dominant_layer
        out.append(_paint(f"ДОМИНИРУЮЩИЙ СЛОЙ: {dominant.name} ({dominant.percentage:.2f}%)", YELLOW, color))
        out.append(f"  Диагностика: {dominant.diagnosis}")
    else:
        out.append(_paint("ДОМИНИРУЮЩИЙ СЛОЙ: не выявлен", YELLOW, color))
    if result.deep:
        deep = result.deep
        out.extend(["", _paint("[4] ГЛУБИННЫЙ ПРОХОД", CYAN, color)])
        repeated = ", ".join(f"{item['word']}×{item['count']}" for item in deep["repeated_patterns"]) or "не выявлены"
        out.append(f"  Повторяющиеся паттерны: {repeated}")
        out.append("  Внутренние противоречия:")
        out.extend(f"    - {item}" for item in deep["contradictions"] or ["не выявлены"])
        out.append("  Рекомендации по очистке:")
        out.extend(f"    - {item}" for item in deep["recommendations"] or ["дополнительные рекомендации не требуются"])
    else:
        out.extend(["", _paint("[4] ГЛУБИННЫЙ ПРОХОД: пропущен (требуется более 100 слов)", DIM, color)])
    out.append(_paint(_line("═"), ORANGE, color))
    return "\n".join(out)


def _read_input(file_path: Optional[str], inline_text: Optional[str]) -> str:
    if file_path and inline_text:
        raise ValueError("Укажите только один источник: файл или --text.")
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    if inline_text is not None:
        return inline_text
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise ValueError("Передайте путь к файлу, --text или текст через stdin.")


def _configure_output() -> None:
    """Включает UTF-8 для кириллицы и палео-разделителей в Windows."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass


def main(argv: Optional[Iterable[str]] = None) -> int:
    _configure_output()
    parser = argparse.ArgumentParser(description="Диагностика текста по слоям подмен методологии «Голем».")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("file", nargs="?", help="UTF-8-файл с текстом")
    source.add_argument("--text", help="Текст для анализа")
    parser.add_argument("--plain", action="store_true", help="Отключить ANSI-цвета")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Вывести структурированный JSON")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        text = _read_input(args.file, args.text)
        result = Analyzer().analyze(text)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    if args.as_json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(_format_report(result, color=not args.plain and sys.stdout.isatty()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())