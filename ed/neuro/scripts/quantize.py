#!/usr/bin/env python3
# ed/neuro/scripts/quantize.py — quantize
# quantize.py — конвертация модели в формат GGUF для локального запуска

import os
import subprocess
import argparse
from pathlib import Path


def find_model_files(model_path: str) -> list:
    """Находит все файлы модели в папке"""
    path = Path(model_path)

    if path.is_file():
        return [str(path)]

    if path.is_dir():
        files = []
        for ext in ['.bin', '.pt', '.pth', '.safetensors', '.gguf']:
            files.extend(path.glob(f'*{ext}'))
        return [str(f) for f in files]

    return []


def check_dependencies() -> bool:
    """Проверяет наличие необходимых инструментов"""
    try:
        result = subprocess.run(
            ['llama-quantize', '--help'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def convert_hf_to_gguf(model_path: str, output_path: str, qtype: str) -> bool:
    """Конвертирует HuggingFace модель в GGUF через convert.py"""
    try:
        cmd = [
            'python', '-m', 'llama_cpp.convert',
            '--model', model_path,
            '--output', output_path.replace('.gguf', '.fp16.gguf'),
            '--outtype', 'f16'
        ]

        print(f"🔄 Конвертация HF -> FP16 GGUF...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Ошибка конвертации: {result.stderr}")
            return False

        temp_path = output_path.replace('.gguf', '.fp16.gguf')
        return quantize_gguf(temp_path, output_path, qtype)

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def quantize_gguf(input_path: str, output_path: str, qtype: str) -> bool:
    """Квантизирует GGUF модель"""
    try:
        cmd = ['llama-quantize', input_path, output_path, qtype]

        print(f"🔄 Квантизация: {qtype}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # Удаляем временный файл
            if input_path != output_path and os.path.exists(input_path):
                os.remove(input_path)
            return True
        else:
            print(f"❌ Ошибка квантизации: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def quantize_with_llama_cpp_python(model_path: str, output_path: str, qtype: str) -> bool:
    """Квантизация через llama-cpp-python"""
    try:
#         from llama_cpp import Llama  # TODO: проверить, используется ли
        from transformers import AutoModelForCausalLM, AutoTokenizer

        print(f"📥 Загрузка модели: {model_path}")
        model = AutoModelForCausalLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        # Сохраняем в временную папку
        temp_dir = Path(output_path).parent / "temp_hf"
        temp_dir.mkdir(exist_ok=True)
        model.save_pretrained(temp_dir)
        tokenizer.save_pretrained(temp_dir)

        # Конвертируем через llama-cpp-python
#         import llama_cpp  # TODO: проверить, используется ли

        print(f"🔄 Конвертация в GGUF...")

#         from llama_cpp.llama import Llama  # TODO: проверить, используется ли
#         from llama_cpp.llama import LlamaCache  # TODO: проверить, используется ли

        cmd = [
            'python', '-m', 'llama_cpp.convert',
            '--model', str(temp_dir),
            '--output', output_path,
            '--quantize', qtype
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Удаляем временную папку
        import shutil
        shutil.rmtree(temp_dir)

        return result.returncode == 0

    except ImportError:
        print("❌ Установите: pip install llama-cpp-python transformers")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Квантизация модели в GGUF формат")
    parser.add_argument("--model_path", type=str, required=True, help="Путь к модели (HF папка или .bin/.pt файл)")
    parser.add_argument("--output_path", type=str, default="models/ed-v1.gguf", help="Путь для выходного GGUF файла")
    parser.add_argument("--qtype", type=str, default="q4_k_m", help="Тип квантизации (q4_k_m, q5_k_m, q8_0, f16)")
    parser.add_argument("--method", type=str, default="auto", choices=["auto", "hf", "gguf"], help="Метод конвертации")

    args = parser.parse_args()

    print("🔄 КВАНТИЗАЦИЯ МОДЕЛИ В GGUF")
    print("============================")
    print(f"Вход: {args.model_path}")
    print(f"Выход: {args.output_path}")
    print(f"Тип: {args.qtype}")
    print("")

    os.makedirs(os.path.dirname(args.output_path), exist_ok=True)

    # Проверяем, не является ли вход уже GGUF
    if args.model_path.endswith('.gguf'):
        if args.model_path == args.output_path:
            print("✅ Файл уже в формате GGUF")
            return

        success = quantize_gguf(args.model_path, args.output_path, args.qtype)

        if success:
            print(f"✅ Квантизация завершена: {args.output_path}")
        else:
            print("❌ Квантизация не удалась")
        return

    # Автоматический выбор метода
    if args.method == "auto":
        if check_dependencies():
            args.method = "gguf"
        else:
            args.method = "hf"

    # Конвертация через HF -> GGUF
    if args.method == "hf":
        success = convert_hf_to_gguf(args.model_path, args.output_path, args.qtype)

    # Конвертация через llama-cpp-python
    elif args.method == "gguf":
        if not check_dependencies():
            print("❌ Установите llama.cpp: https://github.com/ggerganov/llama.cpp")
            print("   или используйте метод 'hf'")
            return
        success = quantize_gguf(args.model_path, args.output_path, args.qtype)

    else:
        print(f"❌ Неизвестный метод: {args.method}")
        return

    if success:
        size = os.path.getsize(args.output_path) / (1024**3)
        print(f"✅ Квантизация завершена")
        print(f"   Размер: {size:.2f} GB")
        print(f"   Путь: {args.output_path}")
    else:
        print("❌ Квантизация не удалась")


if __name__ == "__main__":
    main()
