# 📂 СТРУКТУРА РЕПОЗИТОРИЯ

**Метаданные файла**
- **Файл:** `structure.md`
- **Версия:** 2.3
- **Дата создания:** 2026-05-28
- **Последнее обновление:** 2026-06-05
- **Причина обновления:** Добавлена папка `neural/`, обновлён `.gitignore`, добавлены пояснения для файлов
- **Статус:** Активный
- **Тема:** Полная структура репозитория «Голем» с описанием назначения файлов

---

## 📂 КОРЕНЬ

- `.gitignore` — исключённые файлы (секреты, модели, бэкапы)
- `README.md` — лицо проекта, описание целей и структуры
- `structure.md` — этот файл, структура репозитория
- `BACKLOG.md` — список задач на будущее
- `CHANGELOG.md` — история изменений версий
- `DECISIONS.md` — архитектурные решения и почему они приняты
- `ROADMAP.md` — план развития по вехам
- `TECHNICAL-DEBT.md` — технические долги и проблемы
- `GLOSSARY.md` — краткий глоссарий основных терминов
- `RETROSPECTIVE.md` — ретроспективный анализ и проверка архитектуры
- `drafts/` — черновики
- `ideas/` — идеи для развития
- `instructions/` — инструкции и принципы (для нейросети)
- `neural/` — файлы для локальной нейросети
- `researches/` — исследования явлений
- `terminology/` — разбор терминов
- `tools/` — утилиты для автоматизации

---

## 📁 drafts/

Черновики, временные заметки, неготовый контент.

- `davar-language.md` — черновик языка Давар
- `ideas.md` — старые идеи (перенесены в ideas/)
- `notes.md` — рабочие заметки
- `platform-idea.md` — идея платформы
- `questions.md` — вопросы для исследования

---

## 💡 ideas/

Идеи для развития, нереализованные концепции.

- `cli-checkers.md` — идея чекеров для командной строки
- `paleo-hebrew-dictionary.md` — идея словаря палео-иврита
- `automation-copy-to-md.md` — идея автоматизации копирования
- `project-agent.md` — идея ИИ-агента
- `additional-files.md` — список потенциальных новых файлов
- `web-interface.md` — идея веб-интерфейса
- `visualization-tool.md` — идея визуализации связей
- `gamification.md` — идея геймификации обучения
- `database-schema.md` — схема базы данных
- `search-engine.md` — поисковый движок
- `api-design.md` — дизайн REST API

---

## 📖 instructions/

Инструкции и принципы (критично для настройки нейросети).

- `chat-prompt.md` — шаблон промпта (отправлять первым)
- `manifest.md` — манифест восстановления
- `research-principles.md` — 38 принципов исследований
- `forbidden-words.md` — индекс запрещённых слов
- `research-template.md` — шаблон исследования
- `self-learning-template.md` — шаблон самообучения
- `translation-methodology.md` — методология перевода
- `transliteration-distortions.md` — карта транслитераций
- `tree-method.md` — метод дерева
- `archeology-methodology.md` — археология смыслов
- `hebrew-reconstruction.md` — реконструкция иврита
- `image-map.md` — карта образов
- `images-catalogue.md` — каталог образов
- `retrospective.md` — ретроспектива инструкций
- `neural-network-plan.md` — план нейросети
- `workflow.md` — рабочий процесс
- `coding-standards.md` — стандарты кода
- `collaboration-guide.md` — руководство для контрибьюторов
- `release-process.md` — процесс выпуска версий
- `security-policy.md` — политика безопасности
- `troubleshooting.md` — частые проблемы и решения

### instructions/checkers/

Инструменты проверки текстов.

- `bdikah-checker.md` — проверка на религионизмы
- `mivdak.md` — аудит полезности
- `tikun-fix.md` — задачи по обновлению
- `factcheck.md` — проверка фактов
- `consistency-checker.md` — проверка согласованности

### instructions/exposure/

Методы разоблачения.

- `exposure-principles.md` — основные принципы
- `exposure-methods.md` — 23 метода
- `exposure-mechanisms.md` — механизмы подмены
- `exposure-distortions.md` — типы искажений

### instructions/tahor/

Карты очищения языка (запрещённые слова и замена).

- `religionims.md` — религионизмы
- `grecisms.md` — грецизмы
- `slavicisms.md` — церковнославянизмы
- `latinisms.md` — латинизмы
- `names.md` — имена и названия
- `phrases.md` — фразы и выражения

### instructions/templates/

Шаблоны для создания файлов.

- `concept-analysis-template.md` — шаблон анализа концепции
- `research-template.md` — шаблон исследования
- `self-learning-template.md` — шаблон самообучения

---

## 🧠 neural/

Файлы для локальной нейросети Свидетель (Эд).

- `README.md` — инструкция по использованию
- `training-data/` — данные для обучения
- `models/` — обученные модели (gitignored)
- `inference/` — скрипты для запуска

### neural/training-data/

- `prompts.json` — коллекция промптов для fine-tuning
- `responses.json` — ожидаемые ответы

### neural/models/

- `ed-v1.gguf` — квантованная модель Свидетеля (4-8 GB, gitignored)

### neural/inference/

- `server.py` — сервер для инференса (загружает модель, принимает запросы)
- `client.py` — клиент для отправки запросов к серверу

---

## 🔬 researches/

Исследования явлений, систем, событий, доктрин (130+ файлов).

Каждый файл — разбор конкретной темы с корнями, контекстом, искажениями.

---

## 📚 terminology/

Разбор терминов (80+ файлов).

Каждый файл — одно слово: корень, стихи, искажения, возвращение.

---

## 🛠️ tools/

Утилиты для автоматизации работы с репозиторием.

- `README.md` — инструкция по использованию инструментов
- `menu.py` — единое CLI-меню для всех инструментов
- `check-naming.py` — проверка именования файлов
- `add-metadata.py` — массовое добавление метаданных
- `validate-metadata.py` — проверка корректности метаданных
- `update-versions.py` — обновление версий и дат
- `sync-structure.py` — синхронизация structure.md с файловой системой
- `find-duplicates.py` — поиск дубликатов
- `find-orphans.py` — поиск файлов-сирот
- `check-links.py` — проверка битых ссылок
- `generate-glossary.py` — генерация GLOSSARY.md
- `generate-nav.py` — генерация навигации для README
- `stats-report.py` — генерация статистики в STATS.md
- `export-repo.sh` — выгрузка всех md в один файл
- `backup.sh` — бэкап репозитория
- `create-backup-scheduled.sh` — автоматический бэкап (cron)

### tools/agent/

ИИ-агент для автоматизации (в разработке).

- `agent.py` — главный скрипт агента
- `config.example.yml` — пример конфигурации
- `requirements.txt` — зависимости Python
- `README.md` — инструкция по агенту

---

## ⚖️ ПРАВИЛА

- именование: иврит латиницей через дефис
- формат: Markdown, без таблиц
- иврит + транслитерация + перевод для стихов
- без религионимов в авторской речи
- один md-блок на файл — монолит
- заголовок исследований: эмоджи + пробел + КАПС
