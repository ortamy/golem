#!/usr/bin/env python3
# ed/neuro/scripts/train.py — train
# train.py — fine-tune модели на данных из репозитория

import os
import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
TRAINING_DATA_DIR = REPO_ROOT / "neural" / "training-data"
MODELS_DIR = REPO_ROOT / "neural" / "models"


def prepare_dataset(data_path: str) -> list:
    """Подготавливает датасет из prepared.json"""
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    dataset = []
    for item in data:
        text = f"### Инструкция:\n{item['instruction']}\n\n### Ответ:\n{item['output']}"
        dataset.append({"text": text})

    return dataset


def train_with_transformers(
    model_name: str,
    train_data: list,
    output_dir: str,
    epochs: int,
    batch_size: int,
    learning_rate: float
):
    """Обучение с использованием transformers (требует GPU)"""
    try:
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            TrainingArguments,
            Trainer
        )
        from datasets import Dataset
    except ImportError:
        print("❌ Установите transformers: pip install transformers datasets")
        return None

    print(f"📥 Загрузка модели: {model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=512
        )

    dataset = Dataset.from_list(train_data)
    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        warmup_steps=100,
        logging_steps=10,
        save_steps=500,
        save_total_limit=2,
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        tokenizer=tokenizer
    )

    print("🚀 Начало обучения...")
    trainer.train()

    print("💾 Сохранение модели...")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    return output_dir


def convert_to_gguf(model_path: str, output_path: str, qtype: str = "q4_k_m"):
    """Конвертирует модель в формат GGUF"""
    try:
        import subprocess
        print(f"🔄 Конвертация в GGUF: {model_path} -> {output_path}")

        cmd = [
            "python", "-m", "llama_cpp.convert",
            "--model", model_path,
            "--output", output_path,
            "--quantize", qtype
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Конвертация завершена: {output_path}")
            return output_path
        else:
            print(f"❌ Ошибка конвертации: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("   Установите llama-cpp-python: pip install llama-cpp-python")
        return None


def main():
    parser = argparse.ArgumentParser(description="Fine-tune модели для Свидетеля")
    parser.add_argument("--model_name", type=str, default="meta-llama/Llama-2-7b-hf", help="Базовая модель")
    parser.add_argument("--data_path", type=str, default=str(TRAINING_DATA_DIR / "prepared.json"), help="Путь к данным")
    parser.add_argument("--output_path", type=str, default=str(MODELS_DIR / "ed-v1"), help="Выходная папка")
    parser.add_argument("--epochs", type=int, default=3, help="Количество эпох")
    parser.add_argument("--batch_size", type=int, default=4, help="Размер батча")
    parser.add_argument("--learning_rate", type=float, default=2e-5, help="Скорость обучения")
    parser.add_argument("--quantize", action="store_true", help="Конвертировать в GGUF после обучения")
    parser.add_argument("--qtype", type=str, default="q4_k_m", help="Тип квантизации (q4_k_m, q5_k_m, q8_0)")

    args = parser.parse_args()

    print("🧠 ОБУЧЕНИЕ МОДЕЛИ ЭД — СВИДЕТЕЛЬ")
    print("=================================")
    print("")

    if not os.path.exists(args.data_path):
        print(f"❌ Файл данных не найден: {args.data_path}")
        print("   Запустите: python prepare_data.py")
        return

    print("1. Загрузка датасета...")
    train_data = prepare_dataset(args.data_path)
    print(f"   Записей: {len(train_data)}")

    print("2. Запуск fine-tune...")
    output_dir = train_with_transformers(
        args.model_name,
        train_data,
        args.output_path,
        args.epochs,
        args.batch_size,
        args.learning_rate
    )

    if output_dir and args.quantize:
        print("")
        gguf_path = str(MODELS_DIR / "ed-v1.gguf")
        convert_to_gguf(output_dir, gguf_path, args.qtype)

    print("")
    print("✅ Обучение завершено")
    print(f"   Модель сохранена: {args.output_path}")

    if args.quantize:
        print(f"   GGUF модель: {MODELS_DIR / 'ed-v1.gguf'}")

    print("")
    print("Запустите сервер:")
    print(f"   python server.py --model {MODELS_DIR / 'ed-v1.gguf'}")


if __name__ == "__main__":
    main()
