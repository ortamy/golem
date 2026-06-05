#!/usr/bin/env python3
# client.py — клиент для отправки запросов к серверу Свидетеля

import argparse
import json
import sys
from typing import Optional

import requests


SERVER_URL = "http://localhost:8000"


def send_prompt(prompt: str, server: str, temperature: float = 0.7, max_tokens: int = 512) -> Optional[str]:
    """Отправляет промпт к серверу и возвращает ответ"""
    url = f"{server}/generate"
    
    payload = {
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("response")
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: сервер не запущен")
        print("   Запустите: python server.py")
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
    print("Введите 'exit' для выхода")
    print("Введите 'clear' для очистки экрана")
    print("")
    
    if not check_health(server):
        print("❌ Сервер не доступен")
        print("   Запустите: python server.py")
        return
    
    print("✅ Сервер доступен")
    print("")
    
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
    
    print(f"📋 Обработка {len(prompts)} промптов")
    print("")
    
    for i, prompt in enumerate(prompts, 1):
        print(f"[{i}/{len(prompts)}] {prompt[:50]}...")
        response = send_prompt(prompt, server)
        
        results.append({
            "prompt": prompt,
            "response": response
        })
        
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


def main():
    parser = argparse.ArgumentParser(description="Клиент для сервера Свидетеля")
    parser.add_argument("--prompt", "-p", type=str, help="Промпт для отправки")
    parser.add_argument("--file", "-f", type=str, help="Файл с промптами (по одному на строку)")
    parser.add_argument("--output", "-o", type=str, help="Файл для сохранения результатов (для batch режима)")
    parser.add_argument("--server", "-s", type=str, default=SERVER_URL, help="URL сервера")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Температура (0-1)")
    parser.add_argument("--max-tokens", "-m", type=int, default=512, help="Максимум токенов в ответе")
    parser.add_argument("--interactive", "-i", action="store_true", help="Интерактивный режим")
    
    args = parser.parse_args()
    
    if args.interactive:
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
