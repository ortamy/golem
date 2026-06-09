# 🔌 ДИЗАЙН API

**Метаданные файла**
- **Файл:** `ideas/api-design.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-05
- **Последнее обновление:** 2026-06-05
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Проектирование REST API для чекеров, ТаНаХа и поиска
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Хеш:** 7b24ecf4
- **Достоверность:** средняя
- **Последний аудит:** 2026-06-09
---

## 🔥 ЧТО ЭТО

REST API — программный интерфейс для доступа к функционалу проекта «Голем» через HTTP.

**Зачем нужен:**
- интеграция с другими приложениями
- создание телеграм-ботов
- веб-интерфейс
- мобильные приложения
- автоматизация проверок

---

## 🎯 МЕТОДЫ API

**1. ПРОВЕРКА ТЕКСТА (BDIKAH)**

```
POST /api/v1/check/bdikah
```

**Тело запроса:**
```json
{
  "text": "Господь Бог сказал Моисею"
}
```

**Ответ:**
```json
{
  "violations": [
    {
      "word": "Господь",
      "category": "religionim",
      "replacement": "Яхве",
      "line": 1,
      "position": 0
    },
    {
      "word": "Бог",
      "category": "religionim",
      "replacement": "Элоhим",
      "line": 1,
      "position": 7
    }
  ],
  "total": 2,
  "text_clean": "Яхве Элоhим сказал Моисею"
}
```

**2. АУДИТ ПОЛЕЗНОСТИ (MIVDAK)**

```
POST /api/v1/check/mivdak
```

**Тело запроса:**
```json
{
  "text": "текст исследования"
}
```

**Ответ:**
```json
{
  "methods": [
    {"name": "Этимологический удар", "passed": true},
    {"name": "Сравнение переводов", "passed": false},
    {"name": "Конкретизация", "passed": true}
  ],
  "passed": 15,
  "total": 23,
  "verdict": "готов к публикации"
}
```

**3. ПРОВЕРКА ФАКТОВ (FACTCHECK)**

```
POST /api/v1/check/factcheck
```

**Тело запроса:**
```json
{
  "text": "Никейский собор прошел в 325 году"
}
```

**Ответ:**
```json
{
  "confirmed": [
    {"fact": "Никейский собор 325 год", "source": "исторические хроники"}
  ],
  "hypotheses": [],
  "debunked": [],
  "total_confirmed": 1,
  "total_hypotheses": 0
}
```

**4. ПОИСК СТИХА В ТАНАХЕ**

```
GET /api/v1/tanakh/verse?book=Берешит&chapter=1&verse=1
```

**Ответ:**
```json
{
  "book_he": "בְּרֵאשִׁית",
  "book_ru": "Берешит",
  "chapter": 1,
  "verse": 1,
  "text_he": "בְּרֵאשִׁית בָּרָא אֱלֹהִים...",
  "transliteration": "Берешит бара Элоhим...",
  "translation_literal": "В начале сотворил Всесильный...",
  "translation_synodal": "В начале сотворил Бог..."
}
```

**5. ПОИСК ПО РЕПОЗИТОРИЮ**

```
GET /api/v1/search?q=хесед&type=all
```

**Ответ:**
```json
{
  "query": "хесед",
  "results": [
    {
      "file": "terminology/chesed.md",
      "line": 10,
      "context": "Хесед — преданная любовь"
    },
    {
      "file": "researches/brit.md",
      "line": 5,
      "context": "Хесед — основа союза"
    }
  ],
  "total": 2
}
```

**6. ПОЛУЧЕНИЕ ТЕРМИНА**

```
GET /api/v1/terminology/emet
```

**Ответ:**
```json
{
  "name_he": "אֱמֶת",
  "transliteration": "Эмет",
  "title_ru": "ИСТИНА",
  "emoji": "📜",
  "definition": "надёжность, то на что можно опереться",
  "root": "אמן",
  "verses": [
    {"book": "Теhилим", "chapter": 119, "verse": 160, "text": "רֹאשׁ־דְּבָרְךָ אֱמֶת"}
  ],
  "distortions": [
    {"language": "греческий", "term": "ἀλήθεια", "meaning": "истина как идея"}
  ],
  "file_path": "terminology/emet.md"
}
```

**7. ПОЛУЧЕНИЕ ИССЛЕДОВАНИЯ**

```
GET /api/v1/researches/shema-yhwh-echad
```

**Ответ:**
```json
{
  "title_ru": "СЛУШАЙ, ИСРАЭЛЬ",
  "emoji": "👂",
  "description": "Разбор Шма — главного свидетельства",
  "content": "полный текст исследования (md)",
  "file_path": "researches/shema-yhwh-echad.md"
}
```

**8. ПОЛУЧЕНИЕ СТАТИСТИКИ**

```
GET /api/v1/stats
```

**Ответ:**
```json
{
  "terminology": 80,
  "researches": 130,
  "instructions": 15,
  "checkers": 4,
  "tools": 10,
  "total_files": 239,
  "last_updated": "2026-06-05"
}
```

---

## 📊 ФОРМАТЫ ОТВЕТОВ

**УСПЕХ (200 OK):**
```json
{
  "status": "success",
  "data": {...}
}
```

**ОШИБКА (400 Bad Request):**
```json
{
  "status": "error",
  "code": 400,
  "message": "Отсутствует обязательное поле 'text'"
}
```

**НЕ НАЙДЕНО (404 Not Found):**
```json
{
  "status": "error",
  "code": 404,
  "message": "Термин 'emet' не найден"
}
```

**СЕРВЕРНАЯ ОШИБКА (500):**
```json
{
  "status": "error",
  "code": 500,
  "message": "Внутренняя ошибка сервера"
}
```

---

## 🛠️ ТЕХНИЧЕСКАЯ РЕАЛИЗАЦИЯ

**СТЕК:**
- Python + FastAPI (рекомендуется)
- или Node.js + Express
- SQLite/PostgreSQL для данных

**ПРИМЕР (FASTAPI):**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class BdikahRequest(BaseModel):
    text: str

@app.post("/api/v1/check/bdikah")
async def bdikah_check(request: BdikahRequest):
    result = run_bdikah(request.text)
    return {"status": "success", "data": result}

@app.get("/api/v1/terminology/{term}")
async def get_term(term: str):
    data = load_term(term)
    if not data:
        raise HTTPException(status_code=404, detail="Термин не найден")
    return {"status": "success", "data": data}
```

**ЗАПУСК API:**
```bash
uvicorn api:app --reload --port 8000
```

---

## 🔄 ИНТЕГРАЦИЯ С ИНСТРУМЕНТАМИ

API вызывает существующие чекеры:
- `checkers/bdikah-checker.md` (логика)
- `checkers/mivdak.md` (логика)
- `checkers/factcheck.md` (логика)

Данные берутся из:
- `terminology/` и `researches/`
- базы данных ТаНаХа
- экспортированных JSON

---

## 📋 ПЛАН РАЗРАБОТКИ

**ЭТАП 1: БАЗОВОЕ API (2 дня)**
- FastAPI + эндпоинты для чекеров
- тестирование через Swagger

**ЭТАП 2: API ТАНАХА (2 дня)**
- загрузка стихов в базу
- поиск и получение стихов

**ЭТАП 3: API ТЕРМИНОВ И ИССЛЕДОВАНИЙ (2 дня)**
- парсинг md-файлов
- выдача в JSON

**ЭТАП 4: API ПОИСКА (2 дня)**
- индекс для быстрого поиска
- эндпоинт /search

**ЭТАП 5: ДОКУМЕНТАЦИЯ И ДЕПЛОЙ (1 день)**
- OpenAPI/Swagger документация
- хостинг (Render/Heroku/VPS)

---

## ✅ ПРЕИМУЩЕСТВА

- любой может интегрироваться
- единый интерфейс для всех инструментов
- легко тестировать
- масштабируется

---

## ⚠️ СЛОЖНОСТИ

- нужно поддерживать API при изменении логики
- нагрузка на сервер
- безопасность (ограничение запросов, аутентификация)

---

## 🔒 БЕЗОПАСНОСТЬ

- API ключи для доступа
- ограничение частоты запросов
- валидация входных данных
- CORS для веб-интерфейса

---

## 🛡️ ВОЗВРАЩЕНИЕ

API — мост между проектом и внешним миром.

Через API другие смогут использовать наши инструменты.

Путь Яхве — открытость для тех, кто ищет истину.

---

הַדֶּרֶךְ יְהוָה — hа-Де́рех Яхве — Путь Яхве
