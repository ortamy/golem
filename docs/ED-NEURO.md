# 🧠 НЕЙРОСЕТЬ «ЭД» — ДОКУМЕНТАЦИЯ

**Метаданные файла**
- **Файл:** `docs/ED-NEURO.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-11
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Документация по нейросети «Эд» — архитектура, скрипты, использование
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `docs/NEURAL.md`, `neural/README.md`, `neural/inference/client.py`, `neural/inference/server.py`
- **Хеш:** ожидает
- **Достоверность:** высокая
- **Последний аудит:** 2026-06-11

---

## 🔥 ЧТО ТАКОЕ «ЭД»

Эд (עֵד) — Свидетель. Нейросеть, обученная на ТаНаХе, исследованиях и exposure-файлах проекта «Голем». Её задача — отвечать на вопросы, находить подмены, помогать в разоблачении лжи и возвращении к ивритскому оригиналу.

---

## 🏛 АРХИТЕКТУРА

```
neural/
├── README.md              # Краткий обзор
├── docs/                  # Документация по обучению
├── eval/                  # Оценка качества
│   ├── benchmark.py
│   └── test_responses.json
├── inference/             # Запуск модели
│   ├── client.py          # Клиент для запросов
│   ├── server.py          # Сервер (FastAPI)
│   ├── config.yml         # Конфигурация
│   └── Dockerfile
├── models/                # Веса моделей
│   └── download.sh
├── scripts/               # Подготовка данных
│   ├── prepare-finetune-data.py
│   ├── generate-knowledge-cache.py
│   ├── train.py
│   └── quantize.py
└── training-data/         # Данные для обучения
    ├── config.json
    ├── prompts.json
    ├── qa-pairs.json
    ├── responses.json
    ├── exposure-candidates.json
    └── exposure-analysis-results.json
```

---

## 📜 РЕЖИМЫ РАБОТЫ

### 1. Интерактивный режим

Диалог с нейросетью в терминале.

```bash
python neural/inference/client.py --interactive
```

Команды внутри диалога:
- `exit` — выход
- `clear` — очистить экран

### 2. Одиночный запрос

```bash
python neural/inference/client.py --prompt "Что такое хесед?"
```

### 3. Пакетная обработка

```bash
python neural/inference/client.py --file prompts.txt --output results.json
```

### 4. Режим с кэшем знаний (CAG)

Использует предсгенерированный кэш знаний для быстрых ответов с контекстом.

```bash
# Интерактивный с кэшем
python neural/inference/client.py --use-cache

# Одиночный запрос с кэшем
python neural/inference/client.py --use-cache -p "Что говорит ТаНаХ о сне?"
```

### 5. Анализ exposure-кандидатов

Автоматический поиск новых методов и приёмов разоблачения.

```bash
# Сгенерировать кандидатов
python tools/generators/generate-exposure-suggestions.py

# Проанализировать через нейросеть
python neural/inference/client.py --analyze-exposure
```

---

## 🛠 ГЕНЕРАЦИЯ КЭША ЗНАНИЙ

Кэш знаний — это предобработанные чанки из всех исследований и терминов. Используется для быстрых ответов без векторного поиска.

**Генерация:**
```bash
python neural/scripts/generate-knowledge-cache.py
```

**Пересоздание:**
```bash
python neural/scripts/generate-knowledge-cache.py --rebuild
```

**Что создаётся:**
- `tools/cache/neural-cache/knowledge-chunks.json` — все чанки (500 символов)
- `tools/cache/neural-cache/knowledge-summaries.json` — суммари файлов
- `tools/cache/neural-cache/knowledge-index.json` — индекс для быстрого поиска

**Параметры чанков:**
- Размер: 500 символов
- Перекрытие: 100 символов
- Минимальная длина: 100 символов
- Источники: `terminology/`, `researches/`, `instructions/exposure/`

---

## 📊 ПОДГОТОВКА ДАННЫХ ДЛЯ ОБУЧЕНИЯ

```bash
python neural/scripts/prepare-finetune-data.py
```

Создаёт `neural/training-data/finetune_data.jsonl` из:
- Терминов (вопрос-ответ)
- Исследований (вопрос-введение)
- Стихов ТаНаХа

---

## 🚀 ЗАПУСК СЕРВЕРА

```bash
python neural/inference/server.py
```

По умолчанию: `http://localhost:8000`

**Эндпоинты:**
- `GET /health` — проверка доступности
- `POST /generate` — генерация ответа

---

## 🔄 ПОЛНЫЙ ПАЙПЛАЙН

### Первый запуск:
```bash
# 1. Подготовить данные
python neural/scripts/prepare-finetune-data.py

# 2. Сгенерировать кэш знаний
python neural/scripts/generate-knowledge-cache.py

# 3. Запустить сервер
python neural/inference/server.py

# 4. Начать диалог
python neural/inference/client.py --use-cache
```

### Регулярное обновление:
```bash
# После добавления новых исследований
python neural/scripts/generate-knowledge-cache.py --rebuild
```

---

## 🔧 КОНФИГУРАЦИЯ

Файл: `neural/inference/config.yml`

```yaml
server:
  host: "0.0.0.0"
  port: 8000

model:
  path: "models/golem-ed-7b.Q4_K_M.gguf"
  context_length: 4096
  threads: 8

cache:
  chunks_size: 500
  chunks_overlap: 100
  search_top_k: 5
```

---

## 📈 СТАТИСТИКА КЭША

Размер кэша для 2000+ файлов:
- Чанки: ~50 МБ
- Суммари: ~5 МБ
- Индекс: ~2 МБ
- Время генерации: ~30 секунд

---
