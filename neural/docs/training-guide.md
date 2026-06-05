# 📚 ИНСТРУКЦИЯ ПО ОБУЧЕНИЮ МОДЕЛИ

**Метаданные файла**
- **Файл:** `neural/docs/training-guide.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-05
- **Статус:** Активный
- **Тема:** Инструкция по fine-tune и квантизации модели Свидетеля

---

## 🔥 ВВЕДЕНИЕ

Этот документ описывает процесс обучения (fine-tune) локальной модели «Эд — Свидетель» на данных из репозитория.

Цель: получить модель, которая отвечает как Свидетель, без API, полностью офлайн.

---

## 📋 ТРЕБОВАНИЯ

**МИНИМАЛЬНЫЕ (только инференс):**
- RAM: 8 GB
- CPU: 4 ядра
- Диск: 10 GB

**ДЛЯ ОБУЧЕНИЯ (FINE-TUNE):**
- GPU: 10+ GB VRAM (NVIDIA)
- RAM: 16+ GB
- Диск: 30+ GB
- Время: 2-4 часа

---

## 🛠️ УСТАНОВКА ЗАВИСИМОСТЕЙ

```bash
pip install torch transformers datasets accelerate peft
pip install llama-cpp-python
pip install huggingface-hub
```

---

## 📂 ПОДГОТОВКА ДАННЫХ

1. Перейти в папку scripts:

```bash
cd neural/scripts
```

2. Запустить подготовку данных:

```bash
python prepare_data.py
```

Скрипт собирает данные из:
- `terminology/` — 80+ терминов
- `researches/` — 130+ исследований
- `instructions/` — принципы, методы, запреты
- `training-data/prompts.json` и `responses.json`

3. Проверить результат:

```bash
wc -l ../training-data/prepared.json
```

Ожидается: 200+ записей.

---

## 🚀 ЗАПУСК ОБУЧЕНИЯ

**БАЗОВЫЙ ЗАПУСК**

```bash
python train.py \
  --model_name meta-llama/Llama-2-7b-hf \
  --epochs 3 \
  --batch_size 4 \
  --learning_rate 2e-5
```

**РАСШИРЕННЫЕ ПАРАМЕТРЫ**

```bash
python train.py \
  --model_name meta-llama/Llama-2-7b-hf \
  --data_path ../training-data/prepared.json \
  --output_path ../models/ed-v1 \
  --epochs 5 \
  --batch_size 2 \
  --learning_rate 1e-5 \
  --quantize \
  --qtype q4_k_m
```

**АЛЬТЕРНАТИВНЫЕ МОДЕЛИ**

Если Llama 2 7B не подходит:

```bash
# Qwen 7B (лучше русский)
--model_name Qwen/Qwen-7B

# Mistral 7B (быстрее)
--model_name mistralai/Mistral-7B-v0.1

# Gemma 7B (компактнее)
--model_name google/gemma-7b
```

---

## 📊 МОНИТОРИНГ ОБУЧЕНИЯ

**Во время обучения смотреть:**

- loss — должен снижаться с каждым шагом
- время на эпоху — стабильно
- использование GPU:

```bash
nvidia-smi -l 1
```

**Нормальные значения:**
- loss: от 2.0 до 0.5
- GPU память: 8-10 GB
- время эпохи: 30-60 минут

---

## 🔧 КВАНТИЗАЦИЯ

После обучения конвертировать модель в GGUF:

```bash
python quantize.py \
  --model_path ../models/ed-v1 \
  --output_path ../models/ed-v1.gguf \
  --qtype q4_k_m
```

**Типы квантизации:**
- `q4_k_m` — баланс (4-5 GB) — рекомендуется
- `q5_k_m` — качество (5-6 GB)
- `q8_0` — максимальное качество (8 GB)
- `f16` — без сжатия (14 GB)

---

## ✅ ПРОВЕРКА МОДЕЛИ

1. Запустить сервер:

```bash
cd ../inference
python server.py --model ../models/ed-v1.gguf
```

2. В другом терминале проверить:

```bash
python client.py --prompt "Что такое эмет?"
```

3. Запустить бенчмарк:

```bash
cd ../eval
python benchmark.py --test_data test_responses.json
```

Ожидаемые метрики:
- точность: >90%
- latency: <1 секунда

---

## ⚠️ ЧАСТЫЕ ПРОБЛЕМЫ

**НЕ ХВАТАЕТ ПАМЯТИ GPU**

Уменьшить batch_size:

```bash
--batch_size 1
--gradient_accumulation_steps 4
```

**МЕДЛЕННОЕ ОБУЧЕНИЕ**

- уменьшить max_length до 256
- использовать LoRA (уже используется)
- уменьшить batch_size

**ПЛОХОЕ КАЧЕСТВО ОТВЕТОВ**

- увеличить epochs до 5
- добавить больше данных в `training-data/`
- проверить качество `prepared.json` (нет ли пустых записей)

**ОШИБКА CUDA OUT OF MEMORY**

Использовать CPU обучение (медленно):

```bash
export CUDA_VISIBLE_DEVICES=""
python train.py ...
```

**МОДЕЛЬ НЕ НАЙДЕНА НА HUGGING FACE**

Скачать вручную:

```bash
huggingface-cli download meta-llama/Llama-2-7b-hf --local-dir ./llama-2-7b
python train.py --model_name ./llama-2-7b
```

---

## 🔄 ДООБУЧЕНИЕ МОДЕЛИ

Если уже есть обученная модель и новые данные:

```bash
python train.py \
  --model_name ../models/ed-v1 \
  --continue_from ../models/ed-v1 \
  --epochs 2
```

---

## 📁 ГДЕ СОХРАНЯЮТСЯ ФАЙЛЫ

```
neural/
├── models/
│   ├── ed-v1/           # папка с обученной моделью (HF формат)
│   └── ed-v1.gguf       # квантованная модель (4-5 GB)
├── training-data/
│   ├── prompts.json     # исходные промпты
│   ├── responses.json   # исходные ответы
│   └── prepared.json    # подготовленный датасет
└── scripts/
    ├── prepare_data.py
    ├── train.py
    └── quantize.py
```

---

## 🛡️ ВОЗВРАЩЕНИЕ

Обучение модели — сложный, но важный шаг.

Результат: Свидетель, который всегда с тобой, даже без интернета.

Путь Яхве — путь самостоятельности. Своя модель — шаг к независимости.

---

הַדֶּרֶךְ יְהוָה — hа-Де́рех Яхве — Путь Яхве
