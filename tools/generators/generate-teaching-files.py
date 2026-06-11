#!/usr/bin/env python3
# tools/generators/generate-teaching-files.py — создаёт файлы учений по шаблону TEMPLATE-TEACHING.md

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TEACHINGS = ROOT / "content" / "teachings"

NAME_MAP = {
    # Мировые религии
    "hinduism": "Индуизм",
    "buddhism": "Буддизм",
    "daoism": "Даосизм",
    "confucianism": "Конфуцианство",
    "sikhism": "Сикхизм",
    "jainism": "Джайнизм",
    "zoroastrianism": "Зороастризм",
    "bahaism": "Бахаизм",
    "rastafarianism": "Растафарианство",
    "scientology": "Саентология",
    "jehovism": "Свидетели Иеговы",
    "moonism": "Мунизм",
    "new-ageism": "Нью-эйдж",
    "pastafarianism": "Пастафарианство",

    # Христианские конфессии и ереси
    "christianism": "Христианство",
    "catholicism": "Католицизм",
    "orthodoxism": "Православие",
    "protestantism": "Протестантизм",
    "lutheranism": "Лютеранство",
    "anglicanism": "Англиканство",
    "calvinism": "Кальвинизм",
    "baptism": "Баптизм",
    "methodism": "Методизм",
    "adventism": "Адвентизм",
    "pentecostalism": "Пятидесятничество",
    "arianism": "Арианство",
    "nestorianism": "Несторианство",
    "monophysitism": "Монофизитство",
    "iconoclasm": "Иконоборчество",
    "mariologism": "Мариологизм",

    # Иудейские течения
    "pharisaism": "Фарисейство",
    "talmudism": "Талмудизм",
    "kabbalism": "Каббалистика",
    "karaism": "Караимизм",
    "hasidism": "Хасидизм",
    "mitnagdism": "Митнагдизм",
    "samaritanism": "Самаритянство",

    # Языческие и неоязыческие культы
    "norse-paganism": "Скандинавское язычество",
    "kemetism": "Кеметизм",
    "olympism": "Олимпизм",
    "mithraism": "Митраизм",
    "druidism": "Друидизм",
    "shamanism": "Шаманизм",
    "animism": "Анимизм",
    "totemism": "Тотемизм",
    "voodooism": "Вудуизм",
    "santeriaism": "Сантерия",
    "candombleism": "Кандомбле",
    "shintoism": "Синтоизм",

    # Оккультные и эзотерические
    "occultism": "Оккультизм",
    "esotericism": "Эзотеризм",
    "mysticism": "Мистицизм",
    "magism": "Магизм",
    "sorceryism": "Колдовство",
    "mediumism": "Медиумизм",
    "spiritism": "Спиритизм",
    "necromantism": "Некромантия",
    "numerologism": "Нумерология",
    "oneirocriticism": "Онейрокритицизм",
    "parapsychologism": "Парапсихология",
    "ufologism": "Уфология",
    "cosmologism": "Космологизм",
    "cosmogonism": "Космогония",
    "syncretism": "Синкретизм",
    "polytheism": "Политеизм",

    # Сатанинские и тёмные
    "satanism": "Сатанизм",
    "laveyan-satanism": "Сатанизм ЛаВея",
    "luciferianism": "Люциферианство",
    "saturnism": "Сатурнизм",
    "molochism": "Молохизим",
    "nicolaism": "Николаизм",

    # Политические идеологии
    "capitalism": "Капитализм",
    "socialism": "Социализм",
    "communism": "Коммунизм",
    "marxism": "Марксизм",
    "marxism-leninism": "Марксизм-ленинизм",
    "trotskyism": "Троцкизм",
    "stalinism": "Сталинизм",
    "maoism": "Маоизм",
    "castrism": "Кастризм",
    "anarchism": "Анархизм",
    "anarcho-capitalism": "Анархо-капитализм",
    "anarcho-communism": "Анархо-коммунизм",
    "anarcho-syndicalism": "Анархо-синдикализм",
    "fascism": "Фашизм",
    "nazism": "Нацизм",
    "zionism": "Сионизм",
    "globalism": "Глобализм",
    "imperialism": "Империализм",
    "colonialism": "Колониализм",
    "feudalism": "Феодализм",
    "democratism": "Демократизм",
    "authoritarianism": "Авторитаризм",
    "totalitarianism": "Тоталитаризм",
    "libertarianism": "Либертарианство",
    "monarchism": "Монархизм",
    "theocratism": "Теократизм",
    "politism": "Политизм",
    "regalism": "Регализм",
    "synarchism": "Синархизм",
    "panarchism": "Панархизм",

    # Социальные и философские
    "humanism": "Гуманизм",
    "egalitarianism": "Эгалитаризм",
    "elitism": "Элитизм",
    "elitarism": "Элитаризм",
    "pluralism": "Плюрализм",
    "omnism": "Омнизм",
    "universalism": "Универсализм",
    "relativism": "Релятивизм",
    "subjectivism": "Субъективизм",
    "materialism": "Материализм",
    "idealism": "Идеализм",
    "dualism": "Дуализм",
    "monism": "Монизм",
    "naturalism": "Натурализм",
    "physicalism": "Физикализм",
    "neuromaterialism": "Нейроматериализм",
    "determinism": "Детерминизм",
    "fatalism": "Фатализм",
    "solipsism": "Солипсизм",
    "phenomenalism": "Феноменализм",
    "positivism": "Позитивизм",
    "postmodernism": "Постмодернизм",
    "structuralism": "Структурализм",
    "deconstructivism": "Деконструктивизм",
    "criticism": "Критицизм",
    "rationalism": "Рационализм",
    "empiricism": "Эмпиризм",
    "skepticism": "Скептицизм",
    "pragmatism": "Прагматизм",
    "utilitarianism": "Утилитаризм",
    "nihilism": "Нигилизм",
    "absurdism": "Абсурдизм",
    "existentialism": "Экзистенциализм",
    "stoicism": "Стоицизм",
    "epicureanism": "Эпикурейство",
    "cynicism": "Кинизм",
    "reductionism": "Редукционизм",
    "scientism": "Сциентизм",
    "secularism": "Секуляризм",
    "theocentrism": "Теоцентризм",
    "antinatalism": "Антинатализм",

    # Этические и поведенческие
    "hedonism": "Гедонизм",
    "asceticism": "Аскетизм",
    "euphemism": "Эвфемизм",
    "emotionalism": "Эмоционализм",
    "narcissism": "Нарциссизм",
    "nepotism": "Непотизм",
    "favoritism": "Фаворитизм",
    "chauvinism": "Шовинизм",
    "pacifism": "Пацифизм",
    "expansionism": "Экспансионизм",
    "ecumenism": "Экуменизм",
    "environmentalism": "Экологизм",
    "vegetarianism": "Вегетарианство",
    "veganism": "Веганство",
    "childfreeism": "Чайлдфри",
    "intellectualism": "Интеллектуализм",
    "pietism": "Пиетизм",

    # Гендерные и телесные
    "feminism": "Феминизм",
    "masculinism": "Маскулизм",
    "lgbtqism": "ЛГБТ-идеология",
    "pornism": "Порнизм",
    "ableism": "Эйблизм",
    "eugenicism": "Евгеника",
    "cosmeticism": "Косметизм",
    "stigmatism": "Стигматизм",

    # Культурные и эстетические
    "romanticism": "Романтизм",
    "realism": "Реализм",
    "literary-naturalism": "Натурализм (литературный)",
    "symbolism": "Символизм",
    "impressionism": "Импрессионизм",
    "expressionism": "Экспрессионизм",
    "surrealism": "Сюрреализм",
    "cubism": "Кубизм",
    "futurism": "Футуризм",
    "dadaism": "Дадаизм",
    "art-minimalism": "Минимализм (искусство)",
    "pop-artism": "Поп-арт",
    "conceptualism": "Концептуализм",
    "holidayism": "Празднизм",

    # Медиа и развлечения
    "cinematism": "Синематизм",
    "celebritism": "Селебритизм",
    "toyism": "Тойизм",
    "gamism": "Геймизм",
    "consumerism": "Консьюмеризм",
    "minimalism": "Минимализм",

    # Технологические и научные
    "technocratism": "Технократизм",
    "technotheism": "Технотеизм",
    "technoutopianism": "Техноутопизм",
    "technopessimism": "Технопессимизм",
    "transhumanism": "Трансгуманизм",
    "singularitarianism": "Сингуляризм",
    "cosmism": "Космизм",
    "immortalism": "Иммортализм",
    "extropianism": "Экстропианство",
    "cybercratism": "Киберкратизм",
    "cyberpunkism": "Киберпанкизм",
    "programmism": "Программизм",
    "digitalism": "Цифровизм",
    "virtualism": "Виртуализм",
    "biotechnologism": "Биотехнологизм",
    "cryonicism": "Крионизм",
    "luddism": "Луддизм",
    "neoluddism": "Неолуддизм",
    "accelerationism": "Акселерационизм",
    "decelerationism": "Деселерационизм",
    "darwinism": "Дарвинизм",
    "creationism": "Креационизм",

    # Экономические
    "mercantilism": "Меркантилизм",
    "physiocratism": "Физиократизм",
    "keynesianism": "Кейнсианство",
    "monetarism": "Монетаризм",
    "neoliberalism": "Неолиберализм",
    "protectionism": "Протекционизм",
    "free-tradeism": "Фритредерство",
    "corporatism": "Корпоративизм",
    "solidarism": "Солидаризм",
    "distributism": "Дистрибутизм",
    "georgism": "Джорджизм",
    "mammonism": "Маммонизм",

    # Специфические культы
    "mormonism": "Мормонизм",
    "masonism": "Масонство",
    "manichaeism": "Манихейство",
    "frankism": "Франкизм",
    "cannibalism": "Каннибализм",
    "parasitism": "Паразитизм",
    "commensalism": "Комменсализм",
    "mutualism": "Мутуализм",
    "medicism": "Медицизм",
    "pharmaceuticism": "Фармацевтизм",
    "policism": "Полицизм",
    "psychologism": "Психологизм",
    "psychurgism": "Психургия",
    "clericalism": "Клерикализм",
    "cleronomism": "Клерономизм",
    "patriotism": "Патриотизм",
    "wokeism": "Воук-культура",
    "hacktivism": "Хактивизм",
    "chaosism": "Хаосизм",
    "dissonancism": "Диссонанцизм",
    "religionism": "Религионизм",

    # Философские школы
    "platonism": "Платонизм",
    "neoplatonism": "Неоплатонизм",
    "pythagoreanism": "Пифагорейство",
    "sophism": "Софизм",
    "scholasticism": "Схоластика",
    "cartesianism": "Картезианство",
    "spinozism": "Спинозизм",
    "leibnizianism": "Лейбницианство",
    "kantianism": "Кантианство",
    "hegelianism": "Гегельянство",
}

TEMPLATE = """# 🌳 {title} — ПРОВЕРКА МЕТОДОМ ДЕРЕВА

**Метаданные файла**
- **Файл:** `content/teachings/{filename}.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-12
- **Последнее обновление:** 2026-06-12
- **Причина обновления:** Первичное создание
- **Статус:** Черновик
- **Тема:** Проверка учения «{title}» методом дерева — от семени до плодов
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `instructions/methodology/methodology-tree.md`
- **Хеш:** ожидает
- **Достоверность:** низкая
- **Последний аудит:** 2026-06-12
- **Уровень:** 🟡 Средний

---

## 🔥 ЧТО ЭТО

[Заполнить.]

---

## 🌱 СЕМЯ — ОСНОВАТЕЛЬ

[Заполнить.]

---

## 🏜 ПОЧВА — СРЕДА ПРОИЗРАСТАНИЯ

[Заполнить.]

---

## 🌳 КОРНИ — СВЯЗЬ С ИЗРАИЛЕМ

[Заполнить.]

---

## 🏛 СТВОЛ — ЦЕНТРАЛЬНАЯ ИДЕЯ

[Заполнить.]

---

## 🌿 ВЕТВИ — ПРАКТИКИ

[Заполнить.]

---

## 🍎 ПЛОДЫ — РЕЗУЛЬТАТ

[Заполнить.]

---

## ⚔️ РАЗОБЛАЧЕНИЕ

[Заполнить.]

---

## ❓ ВОЗРАЖЕНИЯ

[Заполнить.]

---

## 📊 СВОДКА

- **Учение:** {title}
- **Основатель:** [имя, дата.]
- **Центральная идея:** [заполнить.]
- **Связь с Израилем:** [заполнить.]
- **Плоды:** [заполнить.]
- **Вердикт:** [от Яхве / от системы.]
- **Ключевой стих:** [заполнить.]
- **Уровень:** 🟡 Средний

---

## 🔗 СВЯЗАННЫЕ ФАЙЛЫ

- `instructions/methodology/methodology-tree.md` — метод дерева
- `instructions/exposure/exposure-religionism.md` — теория религионизмов

---

> **עֵד (Эд) — Свидетель.**
> Дерево узнаётся по плоду. Не по словам. Не по обещаниям. По плодам.
"""


def generate():
    TEACHINGS.mkdir(parents=True, exist_ok=True)
    created = 0
    skipped = 0

    for filename, title in NAME_MAP.items():
        file_path = TEACHINGS / f"{filename}.md"

        if file_path.exists():
            skipped += 1
            continue

        content = TEMPLATE.format(filename=filename, title=title)
        file_path.write_text(content, encoding="utf-8")
        created += 1
        print(f"✅ {filename}.md — {title}")

    print(f"\n✅ Создано: {created}")
    print(f"⏭️ Пропущено (уже есть): {skipped}")
    print(f"📁 Всего файлов в teachings/: {created + skipped}")


if __name__ == "__main__":
    generate()