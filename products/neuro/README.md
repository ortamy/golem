# 🧠 НЕЙРОСЕТЬ «ЭД» — ЛОКАЛЬНЫЙ СВИДЕТЕЛЬ

**Метаданные файла**
- **Файл:** `neural/README.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-05
- **Статус:** Активный
- **Тема:** Инструкция по запуску локальной модели Свидетеля

---

## 🔥 ЧТО ЭТО

Локальная версия нейросети «Эд» (Свидетель), которая работает без интернета, API ключей и платы.

Преимущества:
- полностью офлайн
- приватно (данные не уходят на сервер)
- бесплатно
- без ограничений по количеству запросов

---

## 📂 СТРУКТУРА

neural/

    README.md                     этот файл

    training-data/
        prompts.json              промпты для обучения
        responses.json            ожидаемые ответы

    models/
        ed-v1.gguf                модель (4-8 GB, gitignored)

    inference/
        server.py                 сервер для инференса
        client.py                 клиент для запросов
        requirements.txt          зависимости Python

    scripts/
        prepare_data.py           подготовка данных из репозитория
        train.py                  обучение модели
        quantize.py               квантизация в GGUF

---

## 🚀 БЫСТРЫЙ СТАРТ

1. УСТАНОВИТЬ ЗАВИСИМОСТИ

```bash
cd neural/inference
pip install -r requirements.txt
```

2. СКАЧАТЬ МОДЕЛЬ

Вариант А — готовая модель:

```bash
cd neural/models
wget https://example.com/ed-v1.gguf
```

Вариант Б — сконвертировать самостоятельно (см. раздел «Обучение»)

3. ЗАПУСТИТЬ СЕРВЕР

```bash
cd neural/inference
python server.py --model ../models/ed-v1.gguf --port 8000
```

4. ОТПРАВИТЬ ЗАПРОС

```bash
python client.py --prompt "Что такое эмет?"
```

Или через curl:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Что такое эмет?"}'
```

---

## 🛠️ КОМАНДЫ ЗАПУСКА

СЕРВЕР:

```bash
python server.py --help
```

Опции:
- --model PATH      путь к модели (по умолчанию: ../models/ed-v1.gguf)
- --port INT        порт (по умолчанию: 8000)
- --host TEXT       хост (по умолчанию: 0.0.0.0)
- --n_ctx INT       контекст в токенах (по умолчанию: 2048)
- --n_threads INT   количество потоков (по умолчанию: 4)

КЛИЕНТ:

```bash
python client.py --help
```

Опции:
- --prompt TEXT     промпт для отправки
- --file PATH       читать промпт из файла
- --server URL      адрес сервера (по умолчанию: http://localhost:8000)
- --interactive     интерактивный режим

ИНТЕРАКТИВНЫЙ РЕЖИМ:

```bash
python client.py --interactive

Что такое хесед?
Хесед — преданная любовь...

Покажи Шма
שְׁמַע יִשְׂרָאֵל...

exit
```

---

## 📚 ОБУЧЕНИЕ МОДЕЛИ

ПОДГОТОВКА ДАННЫХ

```bash
cd neural/scripts
python prepare_data.py
```

Скрипт собирает данные из:
- prompts.json и responses.json
- terminology/ (термины)
- researches/ (исследования)
- instructions/ (принципы и методы)

ОБУЧЕНИЕ (FINE-TUNE)

```bash
python train.py \
  --model_name meta-llama/Llama-2-7b-hf \
  --data_path ../training-data/prepared.json \
  --output_path ../models/ed-v1 \
  --epochs 3 \
  --batch_size 4
```

КВАНТИЗАЦИЯ В GGUF

```bash
python quantize.py \
  --model_path ../models/ed-v1 \
  --output_path ../models/ed-v1.gguf \
  --qtype q4_k_m
```

---

## 🔧 КОНФИГУРАЦИЯ

Файл: inference/config.yml

```yaml
server:
  host: "0.0.0.0"
  port: 8000

model:
  path: "../models/ed-v1.gguf"
  n_ctx: 2048
  n_threads: 4
  temperature: 0.7
  top_p: 0.9
  top_k: 40
  repeat_penalty: 1.1

system_prompt: |
  Ты — עֵד (Эд), Свидетель. Твой путь — идти в истине.
  Ты не религиозный учитель, не богослов, не проповедник.
  Ты спутник и инструмент для разоблачения лжи и возвращения к ивритскому оригиналу ТаНаХа.
```

---

## 🐳 DOCKER

СОБРАТЬ ОБРАЗ

```bash
cd neural/inference
docker build -t ed-inference .
```

ЗАПУСТИТЬ КОНТЕЙНЕР

```bash
docker run -p 8000:8000 -v $(pwd)/../models:/app/models ed-inference
```

---

## 📊 ТЕСТИРОВАНИЕ

```bash
cd neural/eval
pytest benchmark.py
```

Ожидаемые метрики:
- latency: менее 1 секунда на запрос
- accuracy: более 90 процентов на тестовых промптах

---

## ⚠️ ТРЕБОВАНИЯ

МИНИМАЛЬНЫЕ
- RAM: 8 GB
- CPU: 4 ядра
- Диск: 10 GB (с моделью)

РЕКОМЕНДУЕМЫЕ
- RAM: 16 GB
- CPU: 8 ядер
- GPU: 6 GB VRAM (ускоряет в 5-10 раз)

---

## 🚫 ЧАСТЫЕ ПРОБЛЕМЫ

ОШИБКА: модель не найдена
Решение: скачай модель или запусти обучение

ОШИБКА: не хватает памяти
Решение: используй меньшую модель (ed-v1-q4.gguf) или закрой другие программы

МЕДЛЕННЫЙ ОТВЕТ
Решение: уменьши n_ctx, увеличь n_threads, используй GPU

---

## 🔄 ОБНОВЛЕНИЕ МОДЕЛИ

1. собрать новые данные: python scripts/prepare_data.py
2. дообучить модель: python scripts/train.py --continue_from ../models/ed-v1
3. сконвертировать в GGUF: python scripts/quantize.py
4. заменить ed-v1.gguf

---

## 🛡️ ВОЗВРАЩЕНИЕ

Локальная модель — шаг к независимости от систем.

Свидетель всегда с тобой, даже без интернета.

Путь Яхве — путь свободы. Свобода от корпоративных API.

---

הַדֶּרֶךְ יְהוָה — hа-Де́рех Яхве — Путь Яхве
