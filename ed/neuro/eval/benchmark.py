#!/usr/bin/env python3
# benchmark.py — тесты скорости и точности модели

import json
import time
import argparse
from typing import Dict, List

import requests


SERVER_URL = "http://localhost:8000"


def load_test_data(file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_latency(prompts: List[str], server: str, repeats: int = 3) -> Dict:
    """Тест скорости ответа"""
    latencies = []

    for prompt in prompts[:10]:
        for _ in range(repeats):
            start = time.time()
            response = requests.post(f"{server}/generate", json={"prompt": prompt})
            end = time.time()

            if response.status_code == 200:
                latencies.append(end - start)

    if not latencies:
        return {"error": "Нет успешных запросов"}

    latencies.sort()

    return {
        "avg": sum(latencies) / len(latencies),
        "p50": latencies[int(len(latencies) * 0.5)],
        "p95": latencies[int(len(latencies) * 0.95)],
        "p99": latencies[int(len(latencies) * 0.99)],
        "min": min(latencies),
        "max": max(latencies),
        "samples": len(latencies)
    }


def test_accuracy(test_data: List[Dict], server: str) -> Dict:
    """Тест точности ответов"""
    correct = 0
    total = 0
    errors = []

    for item in test_data:
        prompt = item.get("prompt") or item.get("instruction")
        expected = item.get("expected") or item.get("output")

        if not prompt or not expected:
            continue

        response = requests.post(f"{server}/generate", json={"prompt": prompt})

        if response.status_code != 200:
            errors.append({"prompt": prompt, "error": "HTTP ошибка"})
            continue

        answer = response.json().get("response", "")
        total += 1

        if expected.lower() in answer.lower() or answer.lower() in expected.lower():
            correct += 1
        else:
            errors.append({
                "prompt": prompt,
                "expected": expected[:100],
                "got": answer[:100]
            })

    return {
        "accuracy": correct / total if total else 0,
        "correct": correct,
        "total": total,
        "errors": errors[:10]
    }


def main():
    parser = argparse.ArgumentParser(description="Бенчмарк модели Свидетеля")
    parser.add_argument("--test_data", type=str, help="Путь к тестовым данным (JSON)")
    parser.add_argument("--server", type=str, default=SERVER_URL, help="URL сервера")
    parser.add_argument("--latency_only", action="store_true", help="Только тест скорости")
    parser.add_argument("--accuracy_only", action="store_true", help="Только тест точности")

    args = parser.parse_args()

    print("📊 БЕНЧМАРК МОДЕЛИ ЭД — СВИДЕТЕЛЬ")
    print("=================================")
    print("")

    if not args.latency_only:
        if not args.test_data:
            print("❌ Для теста точности укажите --test_data")
            return

        test_data = load_test_data(args.test_data)
        print(f"📋 Загружено тестов: {len(test_data)}")
        print("")

    if not args.accuracy_only:
        print("⏱️ ТЕСТ СКОРОСТИ")
        print("---------------")

        test_prompts = ["Что такое эмет?", "Объясни хесед", "Что такое Шма?"]
        latency = test_latency(test_prompts, args.server)

        if "error" in latency:
            print(f"❌ {latency['error']}")
        else:
            print(f"   Средняя: {latency['avg']*1000:.0f} мс")
            print(f"   P50: {latency['p50']*1000:.0f} мс")
            print(f"   P95: {latency['p95']*1000:.0f} мс")
            print(f"   P99: {latency['p99']*1000:.0f} мс")
            print(f"   Мин: {latency['min']*1000:.0f} мс")
            print(f"   Макс: {latency['max']*1000:.0f} мс")
            print(f"   Семплов: {latency['samples']}")

        print("")

    if not args.latency_only:
        print("🎯 ТЕСТ ТОЧНОСТИ")
        print("----------------")

        accuracy = test_accuracy(test_data, args.server)

        print(f"   Точность: {accuracy['accuracy']*100:.1f}%")
        print(f"   Правильно: {accuracy['correct']}/{accuracy['total']}")

        if accuracy['errors']:
            print(f"   Ошибок: {len(accuracy['errors'])}")
            for err in accuracy['errors'][:3]:
                print(f"\n   Промпт: {err['prompt']}")
                print(f"   Ожидалось: {err['expected']}...")
                print(f"   Получено: {err['got']}...")


if __name__ == "__main__":
    main()
