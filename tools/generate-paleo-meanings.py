#!/usr/bin/env python3
"""Пакетная LLM-сборка возможных палео-переводов.

Использует только квадратный WLC/OSHB слой и последовательности функций букв.
Каждый результат сохраняется со статусом review и требует проверки человеком.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import urllib.error
import urllib.request
from pathlib import Path

BASE_GENERATOR = Path(__file__).with_name("generate-bereshit-paleo.py")
SPEC = importlib.util.spec_from_file_location("paleo_corpus", BASE_GENERATOR)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Не удалось загрузить генератор палео-корпуса")
CORPUS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CORPUS)
BOOKS = CORPUS.BOOKS
DATA_DIR = CORPUS.DATA_DIR
FUNCTIONS = CORPUS.FUNCTIONS
consonants = CORPUS.consonants

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:7b"


def functions_for(hebrew: str) -> str:
    return " ; ".join(
        " → ".join(FUNCTIONS[letter] for letter in word if letter in FUNCTIONS)
        for word in consonants(hebrew).split()
    )


def words_payload(verse: dict) -> list[dict]:
    hebrew_words = consonants(verse["hebrew"]).split()
    paleo_words = str(verse.get("paleo") or "").split()
    return [
        {
            "paleo": paleo_words[index] if index < len(paleo_words) else "",
            "chain": [FUNCTIONS[letter] for letter in word if letter in FUNCTIONS],
        }
        for index, word in enumerate(hebrew_words)
    ]


def ask_model(verse: dict, model: str) -> dict:
    prompt = (
        "Ты собираешь рабочую гипотезу палео-перевода для Research Lab. "
        "Не используй синодальный перевод, религиозные штампы и абстрактные термины. "
        "Опирайся только на квадратный текст и цепочки функций букв ниже. "
        "Верни строго JSON без markdown: {\"words\":[{\"paleo\":\"...\",\"chain\":[\"...\"],\"reading\":\"...\"}],\"verse_reading\":\"...\",\"verse_function\":\"...\",\"confidence\":\"review\"}. "
        "words: каждое входное слово ровно один раз, chain не меняй, reading — образное чтение слова. "
        "Примеры чтения: «знак, который связка направляет к вершине через окно», «сила, текущая в форму». "
        "verse_reading — одно связное предложение, сплетающее слова в образ. verse_function — тезис, что делает стих, не повтор цепочки. "
        "Это рабочая гипотеза, не окончательный перевод.\n\n"
        "Квадратный текст: " + verse["hebrew"] + "\n"
        "Слова и цепочки: " + json.dumps(words_payload(verse), ensure_ascii=False)
    )
    body = json.dumps({"model": model, "prompt": prompt, "stream": False, "format": "json", "options": {"temperature": 0.15}}).encode("utf-8")
    request = urllib.request.Request(OLLAMA_URL, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            payload = json.loads(response.read().decode("utf-8"))
        result = json.loads(payload.get("response", "{}"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, json.JSONDecodeError) as error:
        raise RuntimeError("Ollama недоступна или вернула некорректный JSON: " + str(error)) from error
    if not result.get("verse_reading") or not result.get("verse_function") or not isinstance(result.get("words"), list):
        raise RuntimeError("Модель не вернула обязательные поля meaning-pass")
    expected = words_payload(verse)
    if len(result["words"]) != len(expected):
        raise RuntimeError("meaning-pass вернул неполный или дублированный список слов")
    for index, word in enumerate(result["words"]):
        if word.get("paleo") != expected[index]["paleo"] or word.get("chain") != expected[index]["chain"] or not word.get("reading"):
            raise RuntimeError("meaning-pass изменил цепочку или не дал чтение слова")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", choices=BOOKS.keys())
    parser.add_argument("--limit", type=int, default=0, help="Максимум стихов за запуск; 0 — все")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--overwrite", action="store_true", help="Пересобрать уже созданные review-записи")
    args = parser.parse_args()
    targets = [args.book] if args.book else list(BOOKS)
    done = 0
    for book_id in targets:
        path = DATA_DIR / ("bereshit-1.json" if book_id == "bereshit" else book_id + ".json")
        verses = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for verse in verses:
            if args.limit and done >= args.limit:
                break
            if verse.get("paleo_translation_status") == "verified":
                continue
            if verse.get("paleo_translation_status") == "review" and not args.overwrite:
                continue
            result = ask_model(verse, args.model)
            verse["meaning_pass"] = result
            verse["paleo_translation"] = result["verse_reading"].strip()
            verse["paleo_function"] = result["verse_function"].strip()
            verse["verse_function"] = verse["paleo_function"]
            verse["function"] = verse["paleo_function"]
            verse["paleo_translation_status"] = "review"
            verse["paleo_translation_basis"] = ["WLC/OSHB", "таблица 22 палео-функций Research Lab", "Ollama " + args.model]
            verse["paleo_translation_note"] = "LLM-черновик по WLC/OSHB и палео-функциям; требует человеческой текстологической проверки."
            changed = True
            done += 1
            print(book_id, verse.get("source_book"), verse["chapter"], verse["verse"])
        if changed:
            path.write_text(json.dumps(verses, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.limit and done >= args.limit:
            break
    print("Собрано LLM-черновиков:", done)


if __name__ == "__main__":
    main()