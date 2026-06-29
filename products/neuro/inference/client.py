#!/usr/bin/env python3
# ed/neuro/inference/client.py — client
# neural/inference/client.py — клиент для отправки запросов к серверу Свидетеля
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import requests

SERVER_URL = "http://localhost:8000"
REPO_ROOT = Path(__file__).parent.parent.parent
CACHE_DIR = REPO_ROOT / "tools" / "cache" / "neural-cache"


def send_prompt(prompt: str, server: str, temperature: float = 0.7, max_tokens: int = 512) -> Optional[str]:
    """Отправляет промпт к серверу и возвращает ответ"""
    url = f"{server}/generate"
    payload = {
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response")
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: сервер не запущен. Запустите: python server.py")
        return None
    except requests.exceptions.Timeout:
        print("❌ Ошибка: таймаут ожидания ответа")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def check_health(server: str) -> bool:
    """Проверяет доступность сервера"""
    try:
        response = requests.get(f"{server}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def interactive_mode(server: str):
    """Интерактивный режим диалога"""
    print("🧠 ЭД — СВИДЕТЕЛЬ")
    print("=================")
    print("Введите 'exit' для выхода, 'clear' для очистки экрана\n")

    if not check_health(server):
        print("❌ Сервер не доступен. Запустите: python server.py")
        return

    print("✅ Сервер доступен\n")

    while True:
        try:
            prompt = input("> ").strip()
            if not prompt:
                continue
            if prompt.lower() == "exit":
                print("До свидания")
                break
            if prompt.lower() == "clear":
                print("\n" * 2)
                continue

            response = send_prompt(prompt, server)
            if response:
                print(f"\n{response}\n")
            else:
                print("❌ Не удалось получить ответ\n")

        except KeyboardInterrupt:
            print("\nДо свидания")
            break
        except EOFError:
            break


def batch_mode(server: str, prompts_file: str, output_file: Optional[str] = None):
    """Пакетная обработка промптов из файла"""
    try:
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return

    if not check_health(server):
        print("❌ Сервер не доступен")
        return

    results = []
    print(f"📋 Обработка {len(prompts)} промптов\n")

    for i, prompt in enumerate(prompts, 1):
        print(f"[{i}/{len(prompts)}] {prompt[:50]}...")
        response = send_prompt(prompt, server)
        results.append({"prompt": prompt, "response": response})
        if response:
            print(f"   ✅ Готово")
        else:
            print(f"   ❌ Ошибка")

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Результаты сохранены в {output_file}")
    else:
        print("\n📊 РЕЗУЛЬТАТЫ")
        for r in results:
            print(f"\nПромпт: {r['prompt']}")
            print(f"Ответ: {r['response']}")
            print("-" * 40)


def load_knowledge_cache() -> dict:
    """Загружает кэш знаний из файлов."""
    cache = {"chunks": [], "summaries": [], "index": {}}

    chunks_file = CACHE_DIR / "knowledge-chunks.json"
    summaries_file = CACHE_DIR / "knowledge-summaries.json"
    index_file = CACHE_DIR / "knowledge-index.json"

    if chunks_file.exists():
        with open(chunks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cache["chunks"] = data.get("chunks", [])
            cache["stats"] = data.get("stats", {})

    if summaries_file.exists():
        with open(summaries_file, 'r', encoding='utf-8') as f:
            cache["summaries"] = json.load(f)

    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            cache["index"] = json.load(f)

    return cache


def search_cache(query: str, cache: dict, top_k: int = 5) -> list:
    """Простой поиск по кэшу (без векторной БД — по ключевым словам)."""
    query_lower = query.lower()
    query_words = set(query_lower.split())

    scored = []

    # Ищем в суммари (быстро)
    for summary in cache.get("summaries", []):
        text_lower = summary["text"].lower()
        score = sum(1 for w in query_words if w in text_lower)
        if score > 0:
            scored.append((score * 3, summary["file"], summary["title"], summary["text"]))

    # Ищем в чанках (точнее)
    for chunk in cache.get("chunks", []):
        text_lower = chunk["text"].lower()
        score = sum(1 for w in query_words if w in text_lower)
        if score > 0:
            scored.append((score, chunk["file"], chunk["title"], chunk["text"]))

    # Сортируем по релевантности и убираем дубликаты
    scored.sort(key=lambda x: x[0], reverse=True)
    seen = set()
    unique = []
    for s in scored:
        key = s[3][:100]  # Первые 100 символов текста
        if key not in seen:
            seen.add(key)
            unique.append(s)
        if len(unique) >= top_k:
            break

    return unique


def cached_mode(server: str, prompt: str = None):
    """Режим с использованием кэша знаний."""
    print_header("ЭД — СВИДЕТЕЛЬ (CACHED)", "🧠")

    cache = load_knowledge_cache()

    stats = cache.get("stats", {})
    if stats:
        print(f"📚 Чанков: {stats.get('total_chunks', 0)}")
        print(f"📅 Создан: {stats.get('date', 'неизвестно')[:10]}")
    else:
        print_warning("Кэш не найден или пуст")
        print_hint("Запустите: python neural/scripts/generate-knowledge-cache.py")
        return

    if not check_health(server):
        print("❌ Сервер не доступен")
        return

    print("✅ Готов к запросам\n")

    while True:
        try:
            if prompt:
                query = prompt
                single_shot = True
            else:
                query = input("> ").strip()

            if not query:
                continue
            if query.lower() == "exit":
                print("До свидания")
                break
            if query.lower() == "clear":
                print("\n" * 2)
                continue

            # Ищем в кэше
            results = search_cache(query, cache, top_k=3)

            if results:
                # Формируем контекст из найденного
                context_parts = []
                for score, filepath, title, text in results:
                    context_parts.append(f"[{title}]({filepath}):\n{text[:500]}")

                context = "\n\n---\n\n".join(context_parts)

                # Отправляем с контекстом
                full_prompt = f"""Ты — עֵד (Эд), Свидетель. Отвечай на основе предоставленного контекста из ТаНаХа и исследований.

Контекст:
{context}

Вопрос: {query}

Ответ (на основе контекста, с указанием источников):"""

                response = send_prompt(full_prompt, server, temperature=0.3, max_tokens=512)

                if response:
                    print(f"\n{response}\n")
                    if not single_shot:
                        print(f"📎 Источники: {', '.join(set(r[1] for r in results[:3]))}")
                else:
                    print("❌ Не удалось получить ответ\n")
            else:
                # Ничего не найдено — спрашиваем без контекста
                print("🔍 В кэше не найдено, спрашиваю модель...")
                response = send_prompt(query, server)
                if response:
                    print(f"\n{response}\n")

            if single_shot:
                break

        except KeyboardInterrupt:
            print("\nДо свидания")
            break
        except EOFError:
            break


def analyze_exposure(server: str, candidates_file: Optional[str] = None, output_file: Optional[str] = None):
    """Анализирует кандидаты на новые методы/приёмы через нейросеть."""
    if not candidates_file:
        candidates_file = REPO_ROOT / "neural" / "training-data" / "exposure-candidates.json"

    try:
        with open(candidates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка чтения файла кандидатов: {e}")
        print(f"   Сначала запустите: python tools/generators/generate-exposure-suggestions.py")
        return

    if not check_health(server):
        print("❌ Сервер не доступен")
        return

    candidates = data.get("candidates", [])
    if not candidates:
        print("✅ Нет кандидатов для анализа")
        return

    unique_patterns = {}
    for c in candidates:
        match_lower = c["match"].lower()
        if match_lower not in unique_patterns:
            unique_patterns[match_lower] = c

    print(f"🧠 АНАЛИЗ EXPOSURE-КАНДИДАТОВ")
    print(f"=================================")
    print(f"Всего кандидатов: {len(candidates)}")
    print(f"Уникальных паттернов: {len(unique_patterns)}")
    print(f"Сервер: {server}\n")

    system_prompt = """Ты — עֵד (Эд), Свидетель. Проанализируй кандидаты на новые методы, приёмы, типы искажений для exposure-файлов проекта «Голем».

Для каждого кандидата ответь одной строкой в формате:
НОВЫЙ | УЖЕ ЕСТЬ | <категория> | <краткое описание 1 предложение>

Где категория: distortions, techniques-language, techniques-meaning, techniques-social, techniques-economic, techniques-financial, techniques-historical, techniques-symbolic, techniques-meta, methods, mechanisms, religionism

Существующие типы искажений: подмена категории, юридизация, психологизация, сдвиг действия→эмоция, абстракция, сужение смысла, дуализация, кастрация смысла.

Если кандидат не является приёмом/методом — напиши: НЕТ | - | -

Отвечай ТОЛЬКО строкой для каждого кандидата, без пояснений."""

    pattern_list = list(unique_patterns.values())
    batch_size = 5
    results = []
    new_count = 0

    for batch_start in range(0, len(pattern_list), batch_size):
        batch = pattern_list[batch_start:batch_start + batch_size]

        batch_text = "\n".join([
            f"[{batch_start + j + 1}] Кандидат: {c['match']}\n    Контекст: {c['context'][:200]}\n    Файл: {c['file']}"
            for j, c in enumerate(batch)
        ])

        full_prompt = f"{system_prompt}\n\n{batch_text}"

        batch_num = batch_start // batch_size + 1
        total_batches = (len(pattern_list) - 1) // batch_size + 1
        print(f"📤 Батч {batch_num}/{total_batches} ({len(batch)} кандидатов)...")
        response = send_prompt(full_prompt, server, temperature=0.3, max_tokens=1024)

        if response:
            results.append({"batch": batch_num, "candidates": batch, "response": response})
            new_count += response.count("НОВЫЙ")
            print(f"   ✅ Ответ ({len(response)} символов)")
        else:
            print(f"   ❌ Ошибка")

    if not output_file:
        output_file = REPO_ROOT / "neural" / "training-data" / "exposure-analysis-results.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Результаты сохранены в {output_file}")
    print(f"📊 Новых кандидатов: {new_count}")

    if new_count > 0:
        print(f"💡 Просмотрите файл и добавьте новые приёмы в exposure-файлы вручную")


def print_header(title, emoji="📋"):
    """Простой заголовок без Rich."""
    print(f"\n{emoji} {title}")
    print("=" * 50)


def print_warning(msg):
    print(f"⚠️ {msg}")


def print_hint(msg):
    print(f"💡 {msg}")


def main():
    parser = argparse.ArgumentParser(description="Клиент для сервера Свидетеля")
    parser.add_argument("--prompt", "-p", type=str, help="Промпт для отправки")
    parser.add_argument("--file", "-f", type=str, help="Файл с промптами")
    parser.add_argument("--output", "-o", type=str, help="Файл для сохранения результатов")
    parser.add_argument("--server", "-s", type=str, default=SERVER_URL, help="URL сервера")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Температура")
    parser.add_argument("--max-tokens", "-m", type=int, default=512, help="Максимум токенов")
    parser.add_argument("--interactive", "-i", action="store_true", help="Интерактивный режим")
    parser.add_argument("--analyze-exposure", "-a", action="store_true", help="Анализ exposure-кандидатов через нейросеть")
    parser.add_argument("--candidates", "-c", type=str, help="Файл с кандидатами (JSON)")
    parser.add_argument("--use-cache", "-k", action="store_true", help="Использовать кэш знаний (CAG)")

    args = parser.parse_args()

    if args.use_cache:
        cached_mode(args.server, args.prompt)
    elif args.analyze_exposure:
        analyze_exposure(args.server, args.candidates, args.output)
    elif args.interactive:
        interactive_mode(args.server)
    elif args.file:
        batch_mode(args.server, args.file, args.output)
    elif args.prompt:
        if not check_health(args.server):
            print("❌ Сервер не доступен")
            sys.exit(1)
        response = send_prompt(args.prompt, args.server, args.temperature, args.max_tokens)
        if response:
            print(response)
        else:
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()