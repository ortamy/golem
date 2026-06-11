# 🔒 ПОЛИТИКА БЕЗОПАСНОСТИ (SECURITY POLICY)

**Метаданные файла**
- **Файл:** `instructions/security-policy.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-05
- **Последнее обновление:** 2026-06-05
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Политика безопасности для API ключей, токенов и конфиденциальных данных
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `instructions/security-policy.md`, `terminology/yhwh.md`
- **Хеш:** fbd0303d
- **Достоверность:** средняя
- **Последний аудит:** 2026-06-09
---

## 🔥 ВВЕДЕНИЕ

Проект «Голем» не хранит конфиденциальных данных в репозитории.

Этот документ описывает:
- какие данные нельзя коммитить
- как работать с API ключами
- как защитить токены
- что делать при утечке

---

## 🚫 ЧТО НЕЛЬЗЯ КОММИТИТЬ

**ЗАПРЕЩЕНО:**
- API ключи (DeepSeek, OpenAI, GitHub)
- токены доступа
- пароли
- приватные SSH ключи
- файлы с секретами (`.env`, `secrets.json`, `config.local.yml`)
- персональные данные

**ПРИМЕРЫ ЗАПРЕЩЁННЫХ ФАЙЛОВ:**
- `config.yml` с реальными ключами
- `.env`
- `secrets.json`
- `*.pem`
- `*.key`

---

## ✅ ЧТО МОЖНО КОММИТИТЬ

- примеры конфигурации без ключей
- шаблоны с плейсхолдерами
- публичные SSH ключи
- `config.example.yml` (без реальных данных)

**ПРИМЕР КОРРЕКТНОГО КОНФИГА:**
```yaml
# config.example.yml
github:
  token: "YOUR_GITHUB_TOKEN"
deepseek:
  api_key: "YOUR_DEEPSEEK_API_KEY"
```

---

## 🔧 РАБОТА С API КЛЮЧАМИ

### ЛОКАЛЬНАЯ РАЗРАБОТКА

1. скопировать `config.example.yml` в `config.local.yml`
2. заполнить реальными ключами
3. добавить `config.local.yml` в `.gitignore`
4. использовать `config.local.yml` для работы

```bash
cp tools/agent/config.example.yml tools/agent/config.local.yml
# редактировать config.local.yml
echo "tools/agent/config.local.yml" >> .gitignore
```

### ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (РЕКОМЕНДУЕТСЯ)

```bash
export GITHUB_TOKEN="ghp_xxx"
export DEEPSEEK_API_KEY="sk-xxx"
```

В коде:
```python
import os
token = os.environ.get("GITHUB_TOKEN")
```

### .ENV ФАЙЛ

```bash
# .env (не коммитить!)
GITHUB_TOKEN=ghp_xxx
DEEPSEEK_API_KEY=sk-xxx
```

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 📁 .GITIGNORE

**ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА:**
```
# secrets
.env
*.local.yml
secrets.json
*.key
*.pem
config.local.yml

# backups
*.tar.gz
*.zip
backups/

# temp files
*.tmp
*.log
__pycache__/
*.pyc
```

---

## 🛡️ GitHub SECRETS (ДЛЯ ACTIONS)

Для GitHub Actions использовать Secrets:

1. перейти в Settings → Secrets and variables → Actions
2. добавить секреты:
   - `GITHUB_TOKEN`
   - `DEEPSEEK_API_KEY`

В workflow:
```yaml
- name: Run script
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: python3 script.py
```

---

## ⚠️ ЧТО ДЕЛАТЬ ПРИ УТЕЧКЕ

### ЕСЛИ КЛЮЧ ПОПАЛ В РЕПОЗИТОРИЙ

1. **НЕМЕДЛЕННО** отозвать ключ (через панель управления сервиса)
2. сгенерировать новый ключ
3. удалить ключ из истории Git:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch tools/agent/config.yml" \
     --prune-empty --tag-name-filter cat -- --all
   ```
4. запушить форсированно:
   ```bash
   git push --force --all
   ```
5. уведомить администраторов

### ЕСЛИ КЛЮЧ ПОПАЛ В ЧАТ

- отозвать ключ немедленно
- сгенерировать новый
- удалить сообщение из чата

### ЕСЛИ КЛЮЧ ПОПАЛ В ISSUE ИЛИ PR

- отозвать ключ
- сгенерировать новый
- удалить комментарий или закрыть issue

---

## 🔍 ПРОВЕРКА НА УТЕЧКИ

**АВТОМАТИЧЕСКАЯ ПРОВЕРКА:**
```bash
# поиск потенциальных ключей в репозитории
grep -r "sk-[a-zA-Z0-9]" --include="*.py" --include="*.yml" --include="*.md"
grep -r "ghp_[a-zA-Z0-9]" --include="*.py" --include="*.yml"
grep -r "GITHUB_TOKEN" --include="*.py" --include="*.yml"
```

**ИНСТРУМЕНТЫ ДЛЯ ПРОВЕРКИ:**
- `git-secrets` — предотвращает коммит секретов
- `truffleHog` — ищет секреты в истории
- `gitleaks` — сканирует репозиторий

**УСТАНОВКА GIT-SECRETS:**
```bash
brew install git-secrets
git secrets --install
git secrets --register-aws
```

---

## 📋 ПРОВЕРКИ ПЕРЕД КОММИТОМ

**РУЧНАЯ ПРОВЕРКА:**
- [ ] нет API ключей в коде
- [ ] нет токенов в комментариях
- [ ] нет реальных паролей
- [ ] файлы с секретами в `.gitignore`
- [ ] `config.local.yml` не добавлен

**АВТОМАТИЧЕСКАЯ (pre-commit hook):**
```bash
#!/bin/bash
# .git/hooks/pre-commit

if grep -r "sk-[a-zA-Z0-9]" --include="*.py" --include="*.yml"; then
    echo "❌ Найден DeepSeek API ключ!"
    exit 1
fi

if grep -r "ghp_[a-zA-Z0-9]" --include="*.py" --include="*.yml"; then
    echo "❌ Найден GitHub токен!"
    exit 1
fi
```

---

## 🔐 ДЛЯ АДМИНИСТРАТОРОВ

- все ключи хранить в GitHub Secrets или переменных окружения
- регулярно ротировать ключи (раз в 3 месяца)
- давать минимально необходимые права
- использовать разные ключи для разных сервисов
- логировать доступ к секретам

---

## 🚫 ЗАПРЕЩЕНО

- коммитить реальные ключи
- передавать ключи в чатах
- использовать один ключ для всего
- хранить ключи в README или документации
- игнорировать утечки

---

## 📞 СООБЩЕНИЕ ОБ УТЕЧКЕ

Если вы обнаружили утечку:

1. не коммитьте больше ничего
2. сообщите администратору (создайте issue с меткой `security`)
3. отозовите скомпрометированные ключи

**ОТВЕТСТВЕННЫЕ ЗА БЕЗОПАСНОСТЬ:**
- администраторы репозитория
- владелец проекта

---

## 🔄 ОБНОВЛЕНИЕ ПОЛИТИКИ

Политика безопасности обновляется при:
- появлении новых типов секретов
- изменении процессов разработки
- инцидентах безопасности

---

## 🛡️ ВОЗВРАЩЕНИЕ

Безопасность — ответственность каждого.

Один ключ в репозитории — риски для всех.

Путь Яхве — путь мудрости. Мудрость бережёт доверенное.

---

הַדֶּרֶךְ יְהוָה — hа-Де́рех Яхве — Путь Яхве


---
