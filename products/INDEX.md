# 📑 ИНДЕКС PRODUCTS

**Описание:** Индекс всех продуктов проекта «ГОЛЕМ»

---

## 📊 СТАТИСТИКА

- **Всего продуктов:** 8
- **Активных:** 8
- **Последнее обновление:** 2026-07-16

---

## 🚀 ПРОДУКТЫ

### agents/ - 🤖 Мульти-агентная система
**Статус:** В разработке  
**Назначение:** Автономные агенты для исследования и разоблачения

**Компоненты:**
- [agents/](agents/) - основной код
- [agents/agents/](agents/agents/) - модули агентов (researcher, exposer, collector)
- [docs/](agents/docs/) - документация

**Связи:**
- [tools/](../tools/) - инструменты
- [content/](../content/) - контент
- [data/](../data/) - данные

---

### assistant/ - 💬 Ассистент
**Статус:** В разработке  
**Назначение:** Ассистент для помощи в работе с проектом

**Компоненты:**
- [assistant/](assistant/) - основной код ассистента
- [docs/](assistant/docs/) - документация
- [tests/](assistant/tests/) - тесты

**Связи:**
- [tools/](../tools/) - инструменты
- [content/](../content/) - контент
- [instructions/assistant/](../instructions/assistant/) - инструкции

---

### davar/ - 📝 Язык Давар
**Статус:** В разработке  
**Назначение:** Собственный язык программирования для проекта

**Компоненты:**
- [examples/](davar/examples/) - примеры кода
- [docs/](davar/docs/) - документация
- [tests/](davar/tests/) - тесты
- [davar-architecture.md](davar/davar-architecture.md) - архитектура языка
- [davar-language.md](davar/davar-language.md) - спецификация языка

**Связи:**
- [tools/](../tools/) - инструменты
- [instructions/](../instructions/) - методология

---

### neuro/ - 🧠 Нейросеть Эд
**Статус:** В разработке  
**Назначение:** Нейросеть для анализа и генерации текста

**Компоненты:**
- [docs/](neuro/docs/) - документация
- [eval/](neuro/eval/) - оценка модели
- [inference/](neuro/inference/) - сервер и клиент
- [models/](neuro/models/) - модели
- [scripts/](neuro/scripts/) - скрипты
- [training-data/](neuro/training-data/) - данные для обучения
- [tests/](neuro/tests/) - тесты

**Связи:**
- [tools/](../tools/) - инструменты
- [content/](../content/) - контент для обучения
- [data/](../data/) - данные

---

### tanakh/ - 📜 Танах-продукт
**Статус:** В разработке  
**Назначение:** Интерактивный веб-интерфейс для изучения Танаха

**Компоненты:**
- [tanakh/](tanakh/) - основной код
- [docs/](tanakh/docs/) - документация
- [tests/](tanakh/tests/) - тесты

**Связи:**
- [content/tanakh/](../content/tanakh/) - контент Танаха
- [data/](../data/) - данные
- [tools/](../tools/) - инструменты

---

### telegram-bot/ - 📱 Telegram бот
**Статус:** В разработке  
**Назначение:** Доступ к контенту проекта через Telegram

**Компоненты:**
- [telegram-bot/](telegram-bot/) - основной код бота
- [docs/](telegram-bot/docs/) - документация
- [tests/](telegram-bot/tests/) - тесты

**Связи:**
- [content/](../content/) - контент
- [tools/](../tools/) - инструменты

---

### webapp/ - 🌐 Веб-приложение
**Статус:** В разработке  
**Назначение:** Основное веб-приложение проекта

**Компоненты:**
- [webapp/](webapp/) - основной код
- [docs/](webapp/docs/) - документация
- [tests/](webapp/tests/) - тесты

**Связи:**
- [content/](../content/) - контент
- [data/](../data/) - данные
- [tools/](../tools/) - инструменты

---

### website/ - 🌍 Статический сайт
**Статус:** В разработке  
**Назначение:** Публичный сайт проекта

**Компоненты:**
- [website/](website/) - статические файлы
- [docs/](website/docs/) - документация

**Связи:**
- [content/](../content/) - контент
- [tools/](../tools/) - инструменты сборки

---

### golem-os/ - 💻 Golem OS
**Статус:** В разработке  
**Назначение:** Специализированная ОС для работы с проектом

**Компоненты:**
- [golem-os/](golem-os/) - основной код ОС
- [docs/](golem-os/docs/) - документация
- [tests/](golem-os/tests/) - тесты

**Связи:**
- [tools/](../tools/) - инструменты
- [content/](../content/) - контент

---

## 📊 СТАТИСТИКА ПО ПРОДУКТАМ

### По статусу
- **В разработке:** 8
- **Активных:** 8
- **Завершённых:** 0

### По типу
- **AI/ML:** 2 (agents, neuro)
- **Веб:** 3 (tanakh, webapp, website)
- **Языки:** 1 (davar)
- **Боты:** 1 (telegram-bot)
- **ОС:** 1 (golem-os)

---

## 🔗 СВЯЗИ МЕЖДУ ПРОДУКТАМИ

```
content/ → products/
    ├── terminology/ → webapp/, website/
    ├── tanakh/ → tanakh/, telegram-bot/
    ├── bashah/ → webapp/, website/
    ├── researches/ → webapp/, website/
    └── teachings/ → webapp/, website/

tools/ → products/
    ├── checkers/ → все продукты
    ├── generators/ → все продукты
    └── automation/ → все продукты

data/ → products/
    ├── tanakh-books.json → tanakh/, webapp/
    ├── lxx.json → tanakh/, webapp/
    └── translation.json → webapp/, website/
```

---

## 🛠 ИНСТРУМЕНТЫ ДЛЯ ПРОДУКТОВ

### Сборка
- [tools/build/](../tools/build/) - скрипты сборки
- [tools/deploy/](../tools/deploy/) - скрипты деплоя

### Тестирование
- [tools/checkers/](../tools/checkers/) - проверки
- [tests/](tests/) - тесты продуктов

### Данные
- [data/](../data/) - данные для продуктов
- [tools/sync/](../tools/sync/) - синхронизация

---

## 📝 ПРАВИЛА

1. **Изоляция:** каждый продукт изолирован в своей папке
2. **Зависимости:** зависимости в `requirements.txt` внутри папки продукта
3. **Деплой:** инструкции в `docs/DEPLOY.md`
4. **Тестирование:** тесты в `tests/` внутри продукта
5. **Версионирование:** семантическое версионирование

---

### Локальный запуск
```bash
# Мульти-агенты
python products/agents/main.py

# Ассистент
python products/assistant/assistant.py

# Веб-приложение
cd products/webapp && npm start

# Сайт
cd products/website && npm start
```

### Продакшен
```bash
# Деплой через Docker
docker-compose up -d

# Или через скрипты
python tools/deploy/deploy-all.py
```

---

## 📊 МОНИТОРИНГ

### Логи
- [products/agents/logs/](agents/logs/) - логи агентов
- [products/assistant/logs/](assistant/logs/) - логи ассистента
- [products/neuro/logs/](neuro/logs/) - логи нейросети

### Метрики
- [products/webapp/metrics/](webapp/metrics/) - метрики веб-приложения
- [products/telegram-bot/metrics/](telegram-bot/metrics/) - метрики бота

---

## 🔗 НАВИГАЦИЯ

- [README.md](../README.md) - главная страница
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - архитектура проекта
- [docs/STRUCTURE.md](../docs/STRUCTURE.md) - полная структура
- [tools/](../tools/) - инструменты
- [content/](../content/) - контент
- [data/](../data/) - данные

### По продуктам
- [agents/](agents/) - мульти-агентная система
- [assistant/](assistant/) - ассистент
- [davar/](davar/) - язык Давар
- [neuro/](neuro/) - нейросеть Эд
- [tanakh/](tanakh/) - Танах-продукт
- [telegram-bot/](telegram-bot/) - Telegram бот
- [webapp/](webapp/) - веб-приложение
- [website/](website/) - статический сайт
- [golem-os/](golem-os/) - операционная система

---

## 📝 ПРИМЕЧАНИЯ

1. **Разработка:** все продукты в активной разработке
2. **Интеграция:** продукты интегрируются через общие инструменты
3. **Контент:** все продукты используют контент из content/
4. **Данные:** общие данные хранятся в data/
5. **Деплой:** каждый продукт можно деплоить отдельно