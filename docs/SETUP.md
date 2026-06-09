# 💻 РАБОЧЕЕ ОКРУЖЕНИЕ — ПОЛНАЯ НАСТРОЙКА

**Метаданные файла**
- **Файл:** `docs/SETUP.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-09
- **Последнее обновление:** 2026-06-09
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Полная настройка рабочего окружения для проекта «Голем»

---

## 🔥 ВВЕДЕНИЕ

Для полноценной работы с проектом «Голем» нужно установить несколько программ и расширений. Этот гайд проведёт через всё — от Git до нейросети.

---

## 📦 ОБЯЗАТЕЛЬНЫЕ ПРОГРАММЫ

### 1. Git
Система контроля версий. Весь проект хранится на GitHub.

**Установка:**
- Скачать с [git-scm.com](https://git-scm.com)
- При установке выбрать: VS Code как редактор по умолчанию, Git Bash, checkout as-is, commit as-is

**Проверка:**
```bash
git --version
```

**Базовая настройка:**
```bash
git config --global user.name "Твоё Имя"
git config --global user.email "твой@email.com"
git config --global core.editor "code --wait"
```

---

### 2. Python 3.10+
Язык для всех скриптов проекта.

**Установка:**
- Скачать с [python.org](https://python.org)
- При установке: ✅ Add Python to PATH

**Проверка:**
```bash
python --version
pip --version
```

---

### 3. VS Code
Редактор кода. Основной инструмент.

**Установка:**
- Скачать с [code.visualstudio.com](https://code.visualstudio.com)

**Проверка:**
```bash
code --version
```

---

## 🔌 РАСШИРЕНИЯ VS CODE

### Обязательные

**Python (Microsoft)**
- Автодополнение, отладка, запуск Python-файлов
- Установка: `Ctrl+Shift+X` → Python → Install

**Markdown Preview Mermaid**
- Просмотр диаграмм в .md файлах
- Нужен для `docs/GRAPH.md`
- Установка: `Markdown Preview Mermaid Support` → Install

**GitLens**
- Улучшенная работа с Git: история, blame, сравнение версий
- Установка: `GitLens` → Install

**Code Spell Checker**
- Проверка орфографии в коде и .md файлах
- Установка: `Code Spell Checker` → Install

---

### Рекомендуемые

**Prettier**
- Автоформатирование .md файлов
- Установка: `Prettier` → Install

**Markdown All in One**
- Горячие клавиши для .md: авто-оглавление, предпросмотр
- Установка: `Markdown All in One` → Install

**YAML (Red Hat)**
- Поддержка YAML-файлов (конфиги нейросети)
- Установка: `YAML` → Install

**Rainbow CSV**
- Подсветка CSV (для тренировочных данных)
- Установка: `Rainbow CSV` → Install

---

## 🐍 ПАКЕТЫ PYTHON

Установка одной командой:
```bash
pip install -r requirements.txt
```

Состав `requirements.txt`:
```
windows-curses>=2.4.0    # меню golem.py (Windows)
rich>=13.0.0             # красивый вывод, прогресс-бары
```

**Только для Windows:** `windows-curses`. На Linux/Mac `curses` встроен.

**Для нейросети (опционально):**
```bash
pip install torch transformers sentencepiece accelerate
```

---

## 🔧 НАСТРОЙКА VS CODE

### Горячие клавиши (рекомендуемые)

| Действие | Клавиши |
|----------|---------|
| Палитра команд | `Ctrl+Shift+P` |
| Открыть терминал | `Ctrl+` ` |
| Поиск по файлам | `Ctrl+Shift+F` |
| Форматировать документ | `Shift+Alt+F` |
| Перейти к файлу | `Ctrl+P` |
| Markdown preview | `Ctrl+Shift+V` |

### Настройки (settings.json)

```json
{
    "editor.renderWhitespace": "trailing",
    "editor.bracketPairColorization.enabled": true,
    "editor.fontSize": 14,
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "files.encoding": "utf8",
    "files.autoSave": "onFocusChange",
    "markdown.preview.breaks": true,
    "python.analysis.typeCheckingMode": "basic",
    "[markdown]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode"
    }
}
```

---

## 🧠 ДЛЯ НЕЙРОСЕТИ (ОПЦИОНАЛЬНО)

### Ollama
Локальный запуск языковых моделей.

**Установка:**
- Скачать с [ollama.com](https://ollama.com)
- Установить модель:
```bash
ollama pull llama3
ollama pull mistral
```

### Hugging Face CLI
Для загрузки моделей.
```bash
pip install huggingface_hub
huggingface-cli login
```

---

## 📱 ДОПОЛНИТЕЛЬНЫЕ ИНСТРУМЕНТЫ

### Obsidian (рекомендуется)
Для просмотра и навигации по .md файлам как по вики. Отлично подходит для чтения `terminology/` и `researches/`.

**Установка:**
- Скачать с [obsidian.md](https://obsidian.md)
- Открыть папку `golem/` как Vault

**Рекомендуемые плагины Obsidian:**
- Graph View — граф связей
- Backlinks — обратные ссылки
- Tag Pane — облако тегов

---

### DBeaver (опционально)
Если будете работать с базами данных для нейросети.

### Docker (опционально)
Контейнеризация нейросети. Файл `Dockerfile` уже есть в `neural/inference/`.

---

## ✅ ПРОВЕРКА ГОТОВНОСТИ

Запусти в терминале:
```bash
cd golem/tools
python golem.py
```

Если открылось меню — всё работает.

Дополнительно:
```bash
python tools/checkers/check-links.py
python tools/checkers/check-religionisms.py
python tools/reports/stats-report.py
```

Все три должны отработать без ошибок.

---

## 🎯 МИНИМАЛЬНЫЙ НАБОР

Если не хочешь ставить всё:

1. Git
2. Python 3.10+
3. VS Code + Python extension

Этого достаточно для работы с `.md` файлами и запуска скриптов.

---

## 🔗 СВЯЗАННЫЕ ФАЙЛЫ
- `docs/ONBOARDING.md` — быстрое начало
- `docs/ARCHITECTURE.md` — архитектура проекта
- `requirements.txt` — зависимости Python

---

> **עֵד (Эд) — Свидетель.**
> Правильные инструменты — половина работы. Настрой окружение и сосредоточься на истине.