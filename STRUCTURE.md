<<<<<<< HEAD
# 📂 СТРУКТУРА РЕПОЗИТОРИЯ

**Метаданные файла**
- **Файл:** `STRUCTURE.md`
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
=======
# СТРУКТУРА РЕПОЗИТОРИЯ

**Метаданные файла**
- **Файл:** `STRUCTURE.md`
- **Версия:** 2.4
- **Дата создания:** 2026-05-28
- **Последнее обновление:** 2026-06-06
- **Статус:** Активный
- **Тема:** Полная структура репозитория «Голем»

---

## КОРЕНЬ

- `davar/`
- `instructions/`
- `researches/`
- `terminology/`

## davar/

    - `examples/`
    - `davar-architecture.md`
    - `davar-language.md`

## instructions/

    - `checkers/`
        - `bdikah-checker.md`
        - `consistency-checker.md`
        - `factcheck.md`
        - `mivdak.md`
        - `startup-checklist.md`
        - `tikun-fix.md`
    - `exposure/`
        - `exposure-distortions.md`
        - `exposure-mechanisms.md`
        - `exposure-methods.md`
        - `exposure-principles.md`
    - `methodology/`
        - `archeology-methodology.md`
        - `hebrew-reconstruction.md`
        - `translation-methodology.md`
        - `transliteration-distortions.md`
        - `tree-method.md`
    - `tahor/`
        - `grecisms.md`
        - `latinisms.md`
        - `names.md`
        - `phrases.md`
        - `religionims.md`
        - `slavicisms.md`
    - `templates/`
        - `concept-analysis-template.md`
        - `research-template.md`
        - `self-learning-template.md`
    - `chat-prompt.md`
    - `coding-standards.md`
    - `collaboration-guide.md`
    - `forbidden-words.md`
    - `image-map.md`
    - `images-catalogue.md`
    - `manifest.md`
    - `release-process.md`
    - `research-principles.md`
    - `retrospective.md`
    - `security-policy.md`
    - `troubleshooting.md`
    - `workflow.md`

## researches/

    - `books/`
        - `kissinger-the-world-order.md`
        - `machiavelli-the-prince.md`
    - `companies/`
        - `amazon.md`
        - `blackrock.md`
        - `goldman-sachs.md`
        - `google.md`
        - `ibm.md`
        - `jpmorgan.md`
        - `meta.md`
        - `neuralink.md`
        - `palantir.md`
        - `vanguard.md`
    - `history/`
        - `history-of-banks.md`
        - `history-of-economy.md`
        - `history-of-languages.md`
        - `history-of-medicine.md`
        - `history-of-politics.md`
        - `history-of-prison.md`
        - `history-of-religion.md`
        - `history-of-school.md`
        - `israel-palestine.md`
    - `other/`
        - `allopaty.md`
        - `g-generations.md`
        - `gerewol.md`
        - `hygieia.md`
        - `microplastics.md`
        - `new-year.md`
        - `paracelsus.md`
        - `pedophilia.md`
        - `pornography.md`
        - `psychology.md`
        - `pyramid-bunker.md`
        - `slavs.md`
    - `practices/`
        - `exodus-skills.md`
        - `hebrew-week.md`
        - `natural-garden.md`
    - `systems/`
        - `bavel-mitzrayim-sdom.md`
        - `mitzraim-system.md`
        - `red-mitzrayim.md`
        - `russia-empire.md`
        - `talmud-judaism.md`
        - `vatican.md`
    - `abracadabra.md`
    - `acharayut-support.md`
    - `adonai-origin.md`
    - `apocalypse.md`
    - `armageddon.md`
    - `aseret-hadvarim.md`
    - `atah-not-you.md`
    - `balaam-strategy.md`
    - `body-as-temple.md`
    - `brit-hadashah.md`
    - `brit-nissuin.md`
    - `burning-of-books.md`
    - `catholic-church.md`
    - `chadash-restored.md`
    - `daat-tree.md`
    - `dam-chesed.md`
    - `dam-ve-chesed.md`
    - `dam-yeshua-seal.md`
    - `darchei-tzadikim.md`
    - `derech-ha-gever.md`
    - `derech-ha-nachash.md`
    - `dereh-yhwh.md`
    - `digital-coliseum.md`
    - `drashat-hahar.md`
    - `emunah-self-vs-yhwh.md`
    - `eved-amdut.md`
    - `evening-morning-day.md`
    - `exorcism-myth.md`
    - `galatim-two-systems.md`
    - `gambling-vs-life.md`
    - `ha-mashchit.md`
    - `heart-vs-brain.md`
    - `hebrew-truth.md`
    - `hebrew-vs-languages.md`
    - `hellenization-vs-hebraization.md`
    - `hevel-kayin.md`
    - `immanu-el.md`
    - `ishah-yirat-yhwh.md`
    - `israel-vs-yehudi.md`
    - `keshet.md`
    - `khazars-turks.md`
    - `kol-dmamah-dakah.md`
    - `kotz-sting.md`
    - `lechem-ve-yayin.md`
    - `lev-mind.md`
    - `loss-in-translation.md`
    - `mabbel-recreation.md`
    - `makkot-strikes.md`
    - `maschiah-cruteria.md`
    - `masoretic-text.md`
    - `melech-messenger.md`
    - `mered-refusal.md`
    - `migdal-bavel.md`
    - `minecraft-tanakh.md`
    - `miryam-vs-ishtar.md`
    - `mizmor-23.md`
    - `moadim-yhwh.md`
    - `morashat-israel.md`
    - `mushtarah.md`
    - `nachash-serpent.md`
    - `nicaea-council.md`
    - `nicham-keifa.md`
    - `nicham.md`
    - `niddah.md`
    - `nishmat-chayim.md`
    - `olam-haba.md`
    - `olympic-games.md`
    - `or-tam.md`
    - `paleo-hebrew.md`
    - `philosophemes.md`
    - `planetah-wandering-star.md`
    - `plebs-control.md`
    - `purpose-of-tanakh.md`
    - `rabbinic-judaism.md`
    - `religia-rome.md`
    - `remnant-israel.md`
    - `resurrection-analysis.md`
    - `ruach-fruit.md`
    - `ruchot-infected.md`
    - `satan-adversary.md`
    - `serpent-healing.md`
    - `shaal-u-vikesh.md`
    - `shaul-against-philosophy.md`
    - `shaul-victim.md`
    - `sheerit.md`
    - `shema-yhwh-echad.md`
    - `shemot-yhwh.md`
    - `shirat-hayam.md`
    - `shlavim-yetziah.md`
    - `sifrei-bashakh.md`
    - `sifrei-tanakh.md`
    - `slavic-substrate.md`
    - `sod-hamalchut.md`
    - `state-as-symptom.md`
    - `substitution-of-the-name.md`
    - `talmud-unmasked.md`
    - `tanakh-not-old-testament.md`
    - `tarbut-cult.md`
    - `tfilat-yeshua.md`
    - `theophoric-names.md`
    - `tikvah-tension.md`
    - `time-in-tanakh.md`
    - `tree-language.md`
    - `tzeva-hashamayim.md`
    - `tzohar-window.md`
    - `why-canaan-land.md`
    - `why-people-cant-agree.md`
    - `yegia-kapayim.md`
    - `yegia-ve-koach.md`
    - `yehoshua-research.md`
    - `yetzer-lev.md`

## terminology/

    - `ahava.md`
    - `arum.md`
    - `arur.md`
    - `asur.md`
    - `avar-atid.md`
    - `avodah-zarah.md`
    - `avon.md`
    - `barach.md`
    - `bavel.md`
    - `bayit.md`
    - `beit-ha-mikdash.md`
    - `brit.md`
    - `chamas.md`
    - `cherut.md`
    - `chesed.md`
    - `derech-apayim.md`
    - `derech.md`
    - `el.md`
    - `elil.md`
    - `elilim.md`
    - `emet.md`
    - `emuna.md`
    - `erech-apayim.md`
    - `etz-ha-daat.md`
    - `eved.md`
    - `gerim.md`
    - `gibor.md`
    - `golem.md`
    - `goyim.md`
    - `heichal.md`
    - `het.md`
    - `ivri.md`
    - `karaism.md`
    - `karet.md`
    - `kavod.md`
    - `kehillah.md`
    - `koach.md`
    - `kodesh.md`
    - `kohen-hagadol.md`
    - `kohen.md`
    - `korban.md`
    - `ktav-ivri.md`
    - `lamad.md`
    - `lashon-ha-kodesh.md`
    - `levad.md`
    - `levav.md`
    - `malach.md`
    - `mashiah-peshat.md`
    - `melech.md`
    - `mene-tekel.md`
    - `midbar.md`
    - `mikveh.md`
    - `mishchah.md`
    - `mishkan.md`
    - `mishpat.md`
    - `naaf.md`
    - `nachash.md`
    - `navi.md`
    - `nefesh.md`
    - `neshamah.md`
    - `neshech.md`
    - `nishmah.md`
    - `olam.md`
    - `or-tam.md`
    - `pachad.md`
    - `palaestina.md`
    - `panim.md`
    - `pesel.md`
    - `ra.md`
    - `rapha.md`
    - `resha.md`
    - `ruach-hakodesh.md`
    - `ruach.md`
    - `satan.md`
    - `shabbat.md`
    - `shalom.md`
    - `sheerit.md`
    - `shekel.md`
    - `shem.md`
    - `sheol.md`
    - `shlem-avon.md`
    - `shmitah.md`
    - `tefilah.md`
    - `tohu-va-vohu.md`
    - `torah.md`
    - `tov.md`
    - `tshuva.md`
    - `tvilah.md`
    - `tzedek.md`
    - `yeshuah.md`
    - `yetzer-lev.md`
    - `yhwh-not-religion.md`
    - `yhwh.md`
    - `yir-at-yhwh.md`
    - `yovel.md`
    - `zarak.md`
>>>>>>> 27b9c25 (Инициализация репозитория Голем)
