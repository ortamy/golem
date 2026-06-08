# 🤖 АГЕНТ ДЛЯ АВТОМАТИЗАЦИИ ПРОЕКТА

**Метаданные файла**
- **Файл:** `ideas/project-agent.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-05
- **Последнее обновление:** 2026-06-05
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Концепция агента (на базе DeepSeek API) для автоматического добавления файлов, проверки текста и архитектуры проекта
---

## 🔥 ЧТО ЭТО

Агент — это программа, которая работает на твоём компьютере или сервере, имеет доступ к репозиторию и DeepSeek API, и выполняет задачи по твоему согласованию.

**Роли агента:**
- проверяет новые файлы перед добавлением
- запускает чекеры (bdikah, mivdak, factcheck)
- проверяет архитектуру и именование
- создаёт md-файлы по шаблону
- обновляет structure.md
- запрашивает твоё подтверждение перед каждым действием

---

## 📂 СТРУКТУРА АГЕНТА

```
project-agent/
├── agent.py              # главный скрипт
├── config.yml            # настройки (путь к репозиторию, API ключи)
├── requirements.txt      # зависимости
├── actions/
│   ├── add_file.py       # добавление нового файла
│   ├── check_text.py     # запуск bdikah/mivdak/factcheck
│   ├── check_arch.py     # проверка архитектуры
│   ├── update_structure.py # обновление structure.md
│   └── rename_file.py    # исправление именования
├── utils/
│   ├── git_ops.py        # работа с git (commit, push)
│   ├── parsers.py        # парсинг метаданных
│   └── validators.py     # проверка именования
└── logs/
    └── agent.log
```

---

## ⚙️ КАК РАБОТАЕТ

### РЕЖИМ 1: ПРОВЕРКА НОВОГО ФАЙЛА

Ты даёшь агенту текст (или ссылку на сообщение в чате)

Агент:
1. запускает bdikah (проверка религионимов)
2. запускает mivdak (аудит полезности)
3. запускает factcheck (проверка фактов)
4. проверяет, нет ли дубликата в репозитории
5. показывает тебе результат
6. ждёт твоего подтверждения (✅)
7. создаёт md-файл в нужной папке
8. обновляет structure.md
9. делает git commit

### РЕЖИМ 2: ПРОВЕРКА АРХИТЕКТУРЫ

Ты запускаешь `python agent.py --check-arch`

Агент:
1. сканирует всю файловую систему репозитория
2. сверяет с structure.md
3. проверяет имена файлов по правилам
4. проверяет наличие метаданных
5. выводит отчёт о нарушениях
6. предлагает исправления
7. ждёт подтверждения
8. применяет исправления (переименование, перемещение)
9. обновляет structure.md

### РЕЖИМ 3: МОНИТОРИНГ ЧАТА (ОПЦИОНАЛЬНО)

Агент читает твой чат с DeepSeek (через API или расширение)

Когда я отправляю md-файл (с метаданными), агент:
1. перехватывает сообщение
2. проверяет его
3. показывает тебе предложение: «Добавить файл X?»
4. ты подтверждаешь (или отклоняешь)
5. агент сохраняет

---

## 💻 КОД (ОСНОВНОЙ СКРИПТ)

```python
#!/usr/bin/env python3
# agent.py — главный скрипт агента

import os
import re
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class ProjectAgent:
    def __init__(self, config_path: str = "config.yml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.repo_path = Path(self.config['repo_path'])
        self.dry_run = self.config.get('dry_run', False)
    
    def check_file(self, content: str) -> Dict:
        """Проверяет файл через bdikah, mivdak, factcheck"""
        results = {}
        
        # 1. Извлекаем метаданные
        file_path = self.extract_file_path(content)
        if not file_path:
            return {"error": "Не удалось определить путь файла"}
        
        # 2. Проверка на дубликат
        full_path = self.repo_path / file_path
        if full_path.exists():
            return {"error": f"Файл уже существует: {file_path}"}
        
        # 3. Запуск bdikah (имитация, можно вызвать внешний скрипт)
        results['bdikah'] = self.run_bdikah(content)
        
        # 4. Запуск mivdak
        results['mivdak'] = self.run_mivdak(content)
        
        # 5. Запуск factcheck
        results['factcheck'] = self.run_factcheck(content)
        
        # 6. Проверка именования
        results['naming'] = self.check_naming(file_path)
        
        # 7. Проверка заголовка (эмоджи + КАПС)
        results['header'] = self.check_header(content)
        
        return results
    
    def save_file(self, content: str) -> bool:
        """Сохраняет файл в репозиторий"""
        file_path = self.extract_file_path(content)
        if not file_path:
            return False
        
        full_path = self.repo_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Обновление structure.md
        self.update_structure(file_path)
        
        # Git commit
        if not self.dry_run:
            self.git_commit(file_path)
        
        return True
    
    def check_architecture(self) -> Dict:
        """Проверяет архитектуру репозитория"""
        issues = []
        
        # 1. Сравнение с structure.md
        structure = self.load_structure()
        actual_files = self.scan_repo()
        
        missing_in_structure = actual_files - structure
        missing_in_repo = structure - actual_files
        
        if missing_in_structure:
            issues.append(f"❌ Файлы не отражены в structure.md: {missing_in_structure}")
        
        if missing_in_repo:
            issues.append(f"❌ В structure.md указаны, но отсутствуют: {missing_in_repo}")
        
        # 2. Проверка именования файлов
        for file in actual_files:
            if not self.is_valid_name(file):
                issues.append(f"❌ Неверное именование: {file}")
        
        # 3. Проверка наличия метаданных
        for file in actual_files:
            if not self.has_metadata(file):
                issues.append(f"❌ Нет метаданных: {file}")
        
        return {
            "issues": issues,
            "total_files": len(actual_files),
            "issues_count": len(issues)
        }
    
    def run_bdikah(self, content: str) -> str:
        """Запускает bdikah-чекер"""
        # Вызов внешнего скрипта или встроенная проверка
        # Здесь упрощённая версия
        forbidden = ['Бог', 'Господь', 'грех', 'душа']
        found = [w for w in forbidden if w in content]
        
        if found:
            return f"❌ Найдены религионизмы: {found}"
        return "✅ Религионизмов не найдено"
    
    def extract_file_path(self, content: str) -> Optional[str]:
        """Извлекает путь файла из метаданных"""
        match = re.search(r'Файл:\s*`([^`]+\.md)`', content)
        if not match:
            match = re.search(r'File:\s*`([^`]+\.md)`', content)
        return match.group(1) if match else None
    
    def check_naming(self, file_path: str) -> str:
        """Проверяет имя файла по правилам"""
        name = Path(file_path).stem
        
        # Правило: только латиница, дефис, нижний регистр
        if not re.match(r'^[a-z][a-z\-]*$', name):
            return f"❌ Неверное имя: {name} (только a-z и дефис)"
        
        # Правило: без русских букв
        if re.search(r'[а-яА-Я]', name):
            return f"❌ Русские буквы в имени: {name}"
        
        return "✅ Имя корректно"
    
    def check_header(self, content: str) -> str:
        """Проверяет заголовок (эмоджи + КАПС)"""
        lines = content.split('\n')
        if not lines:
            return "❌ Нет заголовка"
        
        header = lines[0].strip()
        
        # Проверка на эмоджи
        if not re.match(r'^# [\U00010000-\U0010FFFF]', header):
            return "❌ Нет эмоджи в заголовке"
        
        # Проверка на КАПС
        after_emoji = header[3:].strip()
        if after_emoji != after_emoji.upper():
            return "❌ Заголовок не капсом"
        
        return "✅ Заголовок корректен"
    
    def is_valid_name(self, file_path: str) -> bool:
        """Проверяет имя файла (полная версия)"""
        name = Path(file_path).stem
        return bool(re.match(r'^[a-z][a-z\-]*$', name))
    
    def has_metadata(self, file_path: str) -> bool:
        """Проверяет наличие метаданных в файле"""
        full_path = self.repo_path / file_path
        try:
            content = full_path.read_text(encoding='utf-8')
            return '**Метаданные файла**' in content or 'Metadata' in content
        except:
            return False
    
    def scan_repo(self) -> set:
        """Сканирует репозиторий и возвращает все md-файлы"""
        files = set()
        for md_file in self.repo_path.rglob('*.md'):
            rel_path = md_file.relative_to(self.repo_path)
            files.add(str(rel_path).replace('\\', '/'))
        return files
    
    def load_structure(self) -> set:
        """Загружает список файлов из structure.md"""
        structure_path = self.repo_path / 'structure.md'
        if not structure_path.exists():
            return set()
        
        content = structure_path.read_text(encoding='utf-8')
        # Упрощённый парсинг (можно улучшить)
        files = re.findall(r'`([a-z-]+\.md)`', content)
        return set(files)
    
    def update_structure(self, new_file: str):
        """Обновляет structure.md (добавляет новый файл)"""
        structure_path = self.repo_path / 'structure.md'
        # Здесь логика обновления структуры
        pass
    
    def git_commit(self, file_path: str):
        """Делает git commit"""
        os.chdir(self.repo_path)
        subprocess.run(['git', 'add', file_path])
        subprocess.run(['git', 'commit', '-m', f'Add {file_path}'])
        subprocess.run(['git', 'push'])


def main():
    agent = ProjectAgent()
    
    print("🤖 Агент проекта «Голем» запущен")
    print("Доступные команды:")
    print("  --check FILE.md   - проверить файл")
    print("  --save FILE.md    - сохранить файл")
    print("  --check-arch      - проверить архитектуру")
    print("  --monitor         - мониторить чат")
    
    # Здесь логика обработки аргументов командной строки


if __name__ == "__main__":
    main()
```

---

## ⚙️ КОНФИГ (CONFIG.YML)

```yaml
repo_path: "/Users/username/golem"
dry_run: false

github:
  token: "ghp_xxx"
  repo: "username/golem"

deepseek:
  api_key: "sk-xxx"
  model: "deepseek-chat"

checkers:
  bdikah_path: "/Users/username/checkers/bdikah.sh"
  mivdak_path: "/Users/username/checkers/mivdak.sh"
  factcheck_path: "/Users/username/checkers/factcheck.sh"

monitoring:
  enabled: false
  chat_source: "telegram"  # или "deepseek_api"
```

---

## 🚀 КАК ЗАПУСТИТЬ

```bash
# 1. Установка зависимостей
pip install pyyaml requests

# 2. Настроить config.yml

# 3. Проверить архитектуру
python agent.py --check-arch

# 4. Проверить новый файл
python agent.py --check new-file.md

# 5. Сохранить файл (с подтверждением)
python agent.py --save new-file.md --confirm

# 6. Запустить в режиме мониторинга
python agent.py --monitor
```

---

## 🔄 РЕЖИМ С ПОДТВЕРЖДЕНИЕМ

При каждом действии агент показывает:

```
🤖 Агент: Найден новый файл

📄 Путь: terminology/emet.md
📊 Проверка:
  ✅ Религионизмов не найдено
  ✅ Mivdak: 15/23 пройдено
  ✅ Factcheck: 4 подтверждено
  ✅ Именование корректно
  ✅ Заголовок: # 📜 ИСТИНА

❓ Добавить файл в репозиторий? (y/n)
```

Ты отвечаешь `y` — агент сохраняет, коммитит, пушит.

---

## 📊 ВОЗМОЖНЫЕ ЗАДАЧИ ДЛЯ АГЕНТА

- добавить новый файл (после проверки)
- обновить существующий файл
- проверить все файлы на соответствие правилам
- исправить именование (массово)
- добавить метаданные в файлы
- синхронизировать structure.md с реальной структурой
- запустить bdikah на всей папке researches/
- найти дубликаты
- сгенерировать отчёт о состоянии проекта
