# 🔒 ПОЛИТИКА БЕЗОПАСНОСТИ (SECURITY POLICY)

**Метаданные файла**
- **Файл:** `instructions/SECURITY-POLICY.md`
- **Версия:** 1.1
- **Дата создания:** 2026-06-05
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** Добавлен DeepSeek/Cline, обновлены пути, убраны несуществующие файлы
- **Статус:** Активный
- **Тема:** Политика безопасности для API ключей, токенов и конфиденциальных данных
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `instructions/SECURITY-POLICY.md`, `.gitignore`
- **Хеш:** ожидает
- **Достоверность:** средняя
- **Последний аудит:** 2026-06-11

---

## 🔥 ВВЕДЕНИЕ

Проект «Голем» не хранит конфиденциальных данных в репозитории.

Этот документ описывает:
- какие данные нельзя коммитить
- как работать с API ключами (DeepSeek, GitHub)
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
- `.env`
- `secrets.json`
- `*.pem`
- `*.key`
- `ed-neural/inference/config.yml` с реальными ключами
- `config.local.yml`

---

## ✅ ЧТО МОЖНО КОММИТИТЬ

- примеры конфигурации без ключей
- шаблоны с плейсхолдерами
- публичные SSH ключи
- `config.example.yml` (без реальных данных)

**ПРИМЕР КОРРЕКТНОГО КОНФИГА:**
```yaml
# config.example.yml
deepseek:
  api_key: "YOUR_DEEPSEEK_API_KEY"
github:
  token: "YOUR_GITHUB_TOKEN"
```

---

## 🔧 РАБОТА С API КЛЮЧАМИ

### ЛОКАЛЬНАЯ РАЗРАБОТКА

1. скопировать `config.example.yml` в `config.local.yml`
2. заполнить реальными ключами
3. добавить `config.local.yml` в `.gitignore`
4. использовать `config.local.yml` для работы

### ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (РЕКОМЕНДУЕТСЯ)

```bash
export GITHUB_TOKEN="ghp_xxx"
export DEEPSEEK_API_KEY="sk-xxx"
```

В коде:
```python
import os
token = os.environ.get("DEEPSEEK_API_KEY")
```

### DEEPSEEK API ДЛЯ CLINE

API ключ DeepSeek используется в Cline (VS Code). Хранить в настройках Cline, не в файлах проекта.

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
2. добавить секреты: `GITHUB_TOKEN`, `DEEPSEEK_API_KEY`

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
     "git rm --cached --ignore-unmatch config.local.yml" \
     --prune-empty --tag-name-filter cat -- --all
   ```
4. запушить форсированно: `git push --force --all`
5. уведомить администраторов

### ЕСЛИ КЛЮЧ ПОПАЛ В ЧАТ

- отозвать ключ немедленно
- сгенерировать новый
- удалить сообщение из чата

---

## 🔍 ПРОВЕРКА НА УТЕЧКИ

**АВТОМАТИЧЕСКАЯ ПРОВЕРКА:**
```bash
grep -r "sk-[a-zA-Z0-9]" --include="*.py" --include="*.yml" --include="*.md"
grep -r "ghp_[a-zA-Z0-9]" --include="*.py" --include="*.yml"
```

**ИНСТРУМЕНТЫ:**
- `git-secrets` — предотвращает коммит секретов
- `gitleaks` — сканирует репозиторий

---

## 🚫 ЗАПРЕЩЕНО

- коммитить реальные ключи
- передавать ключи в чатах
- использовать один ключ для всего
- хранить ключи в README или документации
- игнорировать утечки

---

## 🛡️ ВОЗВРАЩЕНИЕ

Безопасность — ответственность каждого.

Путь Яхве — путь мудрости. Мудрость бережёт доверенное.