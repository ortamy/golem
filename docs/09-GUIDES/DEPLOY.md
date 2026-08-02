# 🚀 DEPLOY — РАЗВЁРТЫВАНИЕ ПРОЕКТА С НУЛЯ

**Метаданные файла**
- **Файл:** `docs/DEPLOY.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-11
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Развёртывание веб-интерфейса и нейросети с нуля
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `docs/DEPLOY.md`, `web/`, `ed-neural/`, `tools/`
- **Хеш:** ожидает
- **Достоверность:** высокая
- **Последний аудит:** 2026-06-11

---

## 📋 ЧТО РАЗВОРАЧИВАЕМ

- Веб-интерфейс (локально или GitHub Pages)
- Нейросеть «Эд» (локально)
- ИИ-агент (локально)

---

## 🌐 ВЕБ-ИНТЕРФЕЙС

### Локально

```bash
cd web
node server.js
```

Открыть: `http://localhost:8080`

### GitHub Pages (автоматически)

Пуш в `main` → GitHub Actions → деплой на `https://<user>.github.io/golem/`

Настройка: Settings → Pages → Source: GitHub Actions

---

## 🧠 НЕЙРОСЕТЬ «ЭД»

### Установка

```bash
pip install -r requirements.txt
```

### Загрузка модели

```bash
cd ed-neural/models
# Скачать GGUF модель (Mistral 7B / DeepSeek Coder)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### Запуск сервера

```bash
cd ed-neural/inference
python server.py
```

Сервер: `http://localhost:8000`

### Проверка

```bash
python ed-neural/inference/client.py --prompt "Что такое хесед?"
```

---

## 🤖 ИИ-АГЕНТ

### Запуск

```bash
python ed-agent/agent.py
```

### Авто-режим

```bash
python ed-agent/agent.py --auto "проверь всё и исправь"
```

---

## 📊 ГЕНЕРАЦИЯ КЭША ЗНАНИЙ

```bash
python ed-neural/scripts/generate-knowledge-cache.py
```

Создаст `tools/cache/neural-cache/` с чанками всех исследований.

---

## ✅ ПРОВЕРКА ОКРУЖЕНИЯ

```bash
python tools/checkers/check-env.py
```

Покажет что установлено, чего не хватает.

---

## 🔧 ПОЛНЫЙ ПАЙПЛАЙН

```bash
# 1. Проверить окружение
python tools/checkers/check-env.py

# 2. Сгенерировать кэш знаний
python ed-neural/scripts/generate-knowledge-cache.py

# 3. Запустить нейросеть
python ed-neural/inference/server.py

# 4. Запустить веб-интерфейс
cd web && node server.js

# 5. Запустить агента
python ed-agent/agent.py
```

---

## 🔗 СВЯЗАННЫЕ ФАЙЛЫ
- `docs/NEURAL.md`
- `docs/ED-AGENT.md`
- `web/README.md`
- `ed-neural/README.md`