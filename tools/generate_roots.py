import json

# Paleo-Hebrew character mapping
PALEO_MAP = {
    "א": "𐤀", "ב": "𐤁", "ג": "𐤂", "ד": "𐤃", "ה": "𐤄",
    "ו": "𐤅", "ז": "𐤆", "ח": "𐤇", "ט": "𐤈", "י": "𐤉",
    "כ": "𐤊", "ך": "𐤊", "ל": "𐤋", "מ": "𐤌", "ם": "𐤌",
    "נ": "𐤍", "ן": "𐤍", "ס": "𐤎", "ע": "𐤏", "פ": "𐤐",
    "ף": "𐤐", "צ": "𐤑", "ץ": "𐤑", "ק": "𐤒", "ר": "𐤓", "ש": "𐤔", "ת": "𐤕"
}

PALEO_MEANINGS = {
    "𐤀": "бык (сила)", "𐤁": "дом (вместилище)", "𐤂": "верблюд (движение)",
    "𐤃": "дверь (вход)", "𐤄": "дыхание (откровение)", "𐤅": "крюк (связь)",
    "𐤆": "оружие (инструмент)", "𐤇": "ограда (отделение)", "𐤈": "змея (оборачивание)",
    "𐤉": "рука (действие)", "𐤊": "ладонь (удержание)", "𐤋": "посох (направление)",
    "𐤌": "вода (течение)", "𐤍": "рыба (жизни)", "𐤎": "опора (поддержка)",
    "𐤏": "глаз (видение)", "𐤐": "рот (речь)", "𐤑": "игла (отделённость)",
    "𐤒": "крюк (праведность)", "𐤓": "голова (начало)", "𐤔": "зуб (разрушение)",
    "𐤕": "знак (печать)"
}

def get_paleo(root):
    return [PALEO_MAP.get(c, c) for c in root]

def get_paleo_meanings(root):
    return [PALEO_MEANINGS.get(PALEO_MAP.get(c, c), "") for c in root]

existing_roots = ['אב', 'אדם', 'אל', 'אמן', 'אמר', 'אש', 'את', 'בן', 'בנה', 'בר', 'ברך', 'בשר', 
                'גדל', 'גל', 'דבר', 'דין', 'דם', 'דע', 'הלך', 'זבח', 'זכר', 'זרע', 'חטא', 
                'חיה', 'חכם', 'חן', 'חסד', 'טוב', 'טהור', 'יד', 'ידע', 'יהוה', 'יום', 'ישב', 
                'ישר', 'כה', 'כבוד', 'כל', 'כן', 'כפר', 'כתב', 'לב', 'למד', 'לקח', 'מלך', 
                'מלה', 'מעש', 'משח', 'משפט', 'נביא', 'נגד', 'נדר', 'נחה', 'נס', 'נער', 'נפש', 
                'נתן', 'סדר', 'סלה', 'סתר', 'עבר', 'עד', 'עזב', 'עזר', 'עין', 'עלה', 'עם', 
                'ענה', 'עצה', 'עשה', 'עשׂר', 'פדה', 'פחד', 'פלא', 'פתח', 'צדק', 'צוה', 'צור', 
                'צלם', 'קדש', 'קול', 'קום', 'קטל', 'קנה', 'קרב', 'קרא', 'ראש', 'רב', 'ראה', 
                'רפא', 'שׂבע', 'שׂדה', 'שׂמח', 'שׂנא', 'שׂר', 'שׂרף', 'שב', 'שבת', 'שגה', 
                'שדד', 'שוב', 'שום', 'שור', 'שחט', 'שיח', 'שיר', 'שלם', 'שם', 'שמר', 'שנה', 
                'שער', 'שפה', 'שפט', 'שקד', 'שקר', 'שתה', 'תהל', 'תוך', 'תור', 'תורה', 'תכן', 
                'תלמיד', 'תם', 'תעה', 'תפל', 'תקוה', 'תשע']

existing_set = set(existing_roots)

# Generate 173 new roots - unique only
new_roots = [
    # Движение (15)
    {"root": "רץ", "translit": "RZ", "meaning": "бежать, спешить", "image": "Начало силы — бег", "examples": ["רץ — бежал"], "substitutions": []},
    {"root": "נסע", "translit": "NSA", "meaning": "ездить, путешествовать", "image": "Жизнь инструмента — движение", "examples": ["נסע — ехал"], "substitutions": []},
    {"root": "שט", "translit": "ShT", "meaning": "плывать, скользить", "image": "Разрушение направления — плавание", "examples": ["שט — плыл"], "substitutions": []},
    {"root": "קפץ", "translit": "QPT", "meaning": "прыгать, перепрыгивать", "image": "Отделённость речи — прыжок", "examples": ["קפץ — прыгнул"], "substitutions": []},
    {"root": "ברח", "translit": "BRKh", "meaning": "бежать, убегать", "image": "Дом начала силы — бегство", "examples": ["ברח — убежал"], "substitutions": []},
    {"root": "ירד", "translit": "YRD", "meaning": "спускаться, опускаться", "image": "Действие двери — спуск", "examples": ["ירד — спустился"], "substitutions": []},
    {"root": "חפז", "translit": "KhPZ", "meaning": "спешить, торопиться", "image": "Отделение рта — спешка", "examples": ["חפז — спешил"], "substitutions": []},
    {"root": "רזף", "translit": "RZPF", "meaning": "бежать, мчаться", "image": "Начало силы печати — мчание", "examples": ["רזף — мчался"], "substitutions": []},
    {"root": "סעף", "translit": "SAFP", "meaning": "лететь, парить", "image": "Поддержка рта печати — полёт", "examples": ["סעף — летел"], "substitutions": []},
    {"root": "דלף", "translit": "DLF", "meaning": "струиться, капать", "image": "Дверь воды течения — струя", "examples": ["דלף — капал"], "substitutions": []},
    {"root": "רחף", "translit": "RChF", "meaning": "парить, лететь", "image": "Начало воды откровения — парение", "examples": ["רחף — парил"], "substitutions": []},
    {"root": "צפף", "translit": "TsPF", "meaning": "собираться, толпиться", "image": "Праведность печати — толпа", "examples": ["צפף — собрался"], "substitutions": []},
    {"root": "בוקר", "translit": "BKR", "meaning": "искать, находить", "image": "Дом опоры начала — поиск", "examples": ["בוקר — искал"], "substitutions": []},
    {"root": "מרץ", "translit": "MRTs", "meaning": "бежать, спешить", "image": "Вода начала силы — спешка", "examples": ["מרץ — март"], "substitutions": []},
    {"root": "סוס", "translit": "Sus", "meaning": "конь, быстрый", "image": "Поддержка знака силы — конь", "examples": ["סוס — конь"], "substitutions": []},
    
    # Речь (15)
    {"root": "שאל", "translit": "ShAL", "meaning": "спрашивать, просить", "image": "Разрушение силы — вопрос", "examples": ["שאל — спросил"], "substitutions": []},
    {"root": "צעק", "translit": "TsAQ", "meaning": "кричать, вопить", "image": "Праведность знака — крик", "examples": ["צעק — закричал"], "substitutions": []},
    {"root": "לחש", "translit": "LSh", "meaning": "шептать, молчаливый", "image": "Направление зуба — шёпот", "examples": ["לחש — прошептал"], "substitutions": []},
    {"root": "ספר", "translit": "SFR", "meaning": "считать, перечислять", "image": "Поддержка двери — счёт", "examples": ["ספר — считал"], "substitutions": []},
    {"root": "מלל", "translit": "MLL", "meaning": "говорить, речь", "image": "Вода направления — речь", "examples": ["מלל — говорил"], "substitutions": []},
    {"root": "אף", "translit": "AP", "meaning": "нос, дыхание", "image": "Сила рта — резкость", "examples": ["אף — нос"], "substitutions": []},
    {"root": "חטף", "translit": "KhTP", "meaning": "хватать, схватывать", "image": "Отделение знака — хватание", "examples": ["חטף — схватил"], "substitutions": []},
    {"root": "שמע", "translit": "ShMA", "meaning": "слышать, воспринимать", "image": "Разрушение воды — слух", "examples": ["שמע — услышал"], "substitutions": []},
    {"root": "בין", "translit": "BYN", "meaning": "понимать, различать", "image": "Дом жизни воды — понимание", "examples": ["בין — понял"], "substitutions": []},
    {"root": "גלה", "translit": "GLH", "meaning": "открывать, раскрывать", "image": "Движение направления — открытие", "examples": ["גלה — открыл"], "substitutions": []},
    {"root": "קול", "translit": "QL", "meaning": "голос, звук", "image": "Игла направления — голос", "examples": ["קול — голос"], "substitutions": []},
    {"root": "דיבר", "translit": "DBR", "meaning": "говорить, разговаривать", "image": "Дверь дома руки — речь", "examples": ["דיבר — говорил"], "substitutions": []},
    {"root": "מלה", "translit": "MLH", "meaning": "слово, речь", "image": "Вода направления — слово", "examples": ["מלה — слово"], "substitutions": []},
    
    # Чувства (12)
    {"root": "ריח", "translit": "RYH", "meaning": "запах, обоняние", "image": "Начало видения — запах", "examples": ["ריח — запах"], "substitutions": []},
    {"root": "טעם", "translit": "TAM", "meaning": "вкус, привкус", "image": "Оборачивание воды — вкус", "examples": ["טעם — вкус"], "substitutions": []},
    {"root": "נגע", "translit": "NGA", "meaning": "прикосновение, контакт", "image": "Жизнь глаза — прикосновение", "examples": ["נגע — прикоснулся"], "substitutions": []},
    {"root": "רוא", "translit": "RVH", "meaning": "чувствовать, ощущать", "image": "Начало воды — ощущение", "examples": ["רוא — чувствовал"], "substitutions": []},
    {"root": "מרא", "translit": "MRH", "meaning": "показывать, видеть", "image": "Вода начала — показ", "examples": ["מרא — показал"], "substitutions": []},
    {"root": "חוש", "translit": "KhSh", "meaning": "чувствовать, вдохновение", "image": "Откровение зуба — чувство", "examples": ["חוש — ощущение"], "substitutions": []},
    {"root": "תחש", "translit": "TChSh", "meaning": "дуновение, лёгкое", "image": "Знак дыхания — дуновение", "examples": ["תחש — дуновение"], "substitutions": []},
    {"root": "נתש", "translit": "NTSh", "meaning": "чувствовать боль", "image": "Жизнь знака — боль", "examples": ["נתש — почувствовал"], "substitutions": []},
    {"root": "סחב", "translit": "ShVB", "meaning": "тянуть, притягивать", "image": "Поддержка зуба — тяга", "examples": ["סחב — тянул"], "substitutions": []},
    {"root": "משכ", "translit": "MShK", "meaning": "тянуться, жажда", "image": "Вода зуба — притяжение", "examples": ["משכ — тянулся"], "substitutions": []},
    {"root": "רגש", "translit": "RGSh", "meaning": "чувство, эмоция", "image": "Начало жизни — чувство", "examples": ["רגש — чувство"], "substitutions": []},
    
    # Природа (15)
    {"root": "אור", "translit": "AVR", "meaning": "свет, озарение", "image": "Сила дома — свет", "examples": ["אור — свет"], "substitutions": []},
    {"root": "גשם", "translit": "GShM", "meaning": "дождь, осенью", "image": "Движение дома воды — дождь", "examples": ["גשם — дождь"], "substitutions": []},
    {"root": "טל", "translit": "TL", "meaning": "роса, росы", "image": "Оборачивание откровения — роса", "examples": ["טל — роса"], "substitutions": []},
    {"root": "ברק", "translit": "BRQ", "meaning": "молния, вспышка", "image": "Дом начала — молния", "examples": ["ברק — молния"], "substitutions": []},
    {"root": "רעם", "translit": "RAM", "meaning": "гром, раскаты", "image": "Начало воды — гром", "examples": ["רעם — гром"], "substitutions": []},
    {"root": "שמש", "translit": "ShMSh", "meaning": "солнце, сиять", "image": "Разрушение воды — солнце", "examples": ["שמש — солнце"], "substitutions": []},
    {"root": "ירח", "translit": "YRCh", "meaning": "луна, месяц", "image": "Действие руки — луна", "examples": ["ירח — луна"], "substitutions": []},
    {"root": "כוכב", "translit": "KVKh", "meaning": "звезда, светить", "image": "Удержание дома — звезда", "examples": ["כוכב — звезда"], "substitutions": []},
    {"root": "רים", "translit": "RYM", "meaning": "высокий, гора", "image": "Начало видения воды — высота", "examples": ["רים — высокий"], "substitutions": []},
    {"root": "עמק", "translit": "AMK", "meaning": "глубина, бездна", "image": "Видение дома — глубина", "examples": ["עמק — глубина"], "substitutions": []},
    {"root": "בקע", "translit": "BQ", "meaning": "рассекать, простор", "image": "Дом опоры — простор", "examples": ["בקע — рассекал"], "substitutions": []},
    {"root": "רוח", "translit": "RUH", "meaning": "ветер, дух", "image": "Начало дыхания — ветер", "examples": ["רוח — ветер"], "substitutions": []},
    {"root": "שלג", "translit": "ShLG", "meaning": "снег, лед", "image": "Разрушение направления — снег", "examples": ["שלג — снег"], "substitutions": []},
    {"root": "חול", "translit": "KhL", "meaning": "песок, пустыня", "image": "Откровение направления — песок", "examples": ["חול — песок"], "substitutions": []},
    
    # Семья (15)
    {"root": "אם", "translit": "AM", "meaning": "мать, материнство", "image": "Сила воды — мать", "examples": ["אם — мать"], "substitutions": []},
    {"root": "אח", "translit": "AKH", "meaning": "брат, роднушка", "image": "Сила дома — брат", "examples": ["אח — брат"], "substitutions": []},
    {"root": "אחות", "translit": "AKHT", "meaning": "сестра, роднушка", "image": "Сила дома печати — сестра", "examples": ["אחות — сестра"], "substitutions": []},
    {"root": "דוד", "translit": "DVD", "meaning": "любовь, прошение", "image": "Вход дома — прошение", "examples": ["דוד — Давид"], "substitutions": []},
    {"root": "אבא", "translit": "ABA", "meaning": "отец, родоначальник", "image": "Сила дома силы — отец", "examples": ["אבא — папа"], "substitutions": []},
    {"root": "אמא", "translit": "AMA", "meaning": "мать, материнство", "image": "Сила воды воды — мать", "examples": ["אמא — мама"], "substitutions": []},
    {"root": "בת", "translit": "BT", "meaning": "дочь, девушка", "image": "Дверь знака — дочь", "examples": ["בת — дочь"], "substitutions": []},
    {"root": "גיס", "translit": "GYS", "meaning": "свекр, сноха", "image": "Движение жизни — свекр", "examples": ["גיס — свекр"], "substitutions": []},
    {"root": "סב", "translit": "SV", "meaning": "дед, старший", "image": "Поддержка силы — дед", "examples": ["סב — дед"], "substitutions": []},
    {"root": "סבתא", "translit": "SBT", "meaning": "бабушка, старшая", "image": "Поддержка знака — бабушка", "examples": ["סבתא — бабушка"], "substitutions": []},
    {"root": "חמוד", "translit": "KhMD", "meaning": "дети, потомство", "image": "Откровение зуба воды — потомство", "examples": ["חמוד — дети"], "substitutions": []},
    {"root": "זוג", "translit": "ZVG", "meaning": "пара, двойка", "image": "Оружие связи — пара", "examples": ["זוג — пара"], "substitutions": []},
    {"root": "ילד", "translit": "YLD", "meaning": "ребёнок, дитя", "image": "Дверь зуба дома — ребёнок", "examples": ["ילד — ребёнок"], "substitutions": []},
    {"root": "בעל", "translit": "BAL", "meaning": "муж, хозяин", "image": "Дом воды — муж", "examples": ["בעל — муж"], "substitutions": []},
    {"root": "אישה", "translit": "YSKh", "meaning": "жена, женщина", "image": "Сила действия — жена", "examples": ["אישה — жена"], "substitutions": []},
    
    # Время (12)
    {"root": "בקר", "translit": "BQR", "meaning": "утро, рассвет", "image": "Дом опоры — утро", "examples": ["בקר — утро"], "substitutions": []},
    {"root": "צהרים", "translit": "TsHRM", "meaning": "полдень, зенит", "image": "Праведность руки воды — полдень", "examples": ["צהרים — полдень"], "substitutions": []},
    {"root": "ערב", "translit": "ARB", "meaning": "вечер, притаившийся", "image": "Видение дома — вечер", "examples": ["ערב — вечер"], "substitutions": []},
    {"root": "ליל", "translit": "LYL", "meaning": "ночь, тьма", "image": "Направление жизни — ночь", "examples": ["ליל — ночь"], "substitutions": []},
    {"root": "עת", "translit": "AT", "meaning": "мгновение, время", "image": "Видение знака — мгновение", "examples": ["עת — время"], "substitutions": []},
    {"root": "זמן", "translit": "ZMQN", "meaning": "время, период", "image": "Орудие знака — время", "examples": ["זמן — время"], "substitutions": []},
    {"root": "שעה", "translit": "ShAH", "meaning": "час, момент", "image": "Разрушение входа — час", "examples": ["שעה — час"], "substitutions": []},
    {"root": "רגע", "translit": "RGA", "meaning": "мгновение, пора", "image": "Начало жизни — мгновение", "examples": ["רגע — мгновение"], "substitutions": []},
    {"root": "עתיד", "translit": "ATYD", "meaning": "будущее, предстоящее", "image": "Видение знака — будущее", "examples": ["עתיד — будущее"], "substitutions": []},
    {"root": "זהר", "translit": "ZhR", "meaning": "свет, рассвет", "image": "Оружие начала — свет", "examples": ["זהר — свет"], "substitutions": []},
    
    # Качества (15)
    {"root": "חזק", "translit": "HZQ", "meaning": "сильный, крепкий", "image": "Отделение знака — сила", "examples": ["חזק — сильный"], "substitutions": []},
    {"root": "חלש", "translit": "HLSH", "meaning": "слабый, немощный", "image": "Отделение змеи — слабость", "examples": ["חלש — слабый"], "substitutions": []},
    {"root": "מהיר", "translit": "MHR", "meaning": "быстрый, скорый", "image": "Вода силы — скорость", "examples": ["מהיר — быстрый"], "substitutions": []},
    {"root": "איטי", "translit": "ATY", "meaning": "медленный, замедленный", "image": "Сила знака — медленность", "examples": ["איטי — медленный"], "substitutions": []},
    {"root": "גדול", "translit": "GDL", "meaning": "великий, большой", "image": "Движение входа — величие", "examples": ["גדול — великий"], "substitutions": []},
    {"root": "קטן", "translit": "QTN", "meaning": "маленький, крошечный", "image": "Отделённость воды — малыш", "examples": ["קטן — маленький"], "substitutions": []},
    {"root": "יפה", "translit": "YPA", "meaning": "красивый, прекрасный", "image": "Действие рта — красота", "examples": ["יפה — красивый"], "substitutions": []},
    {"root": "כי", "translit": "KI", "meaning": "как, потому что", "image": "Ладонь силы — причина", "examples": ["כי — потому что"], "substitutions": []},
    {"root": "אמין", "translit": "AMYN", "meaning": "надёжный, верный", "image": "Сила воды — надёжность", "examples": ["אמין — надёжный"], "substitutions": []},
    {"root": "נבון", "translit": "NVYN", "meaning": "разумный, умный", "image": "Жизнь двери — разум", "examples": ["נבון — разумный"], "substitutions": []},
    {"root": "כסף", "translit": "KSP", "meaning": "серебро, ценность", "image": "Удержание ограды — ценность", "examples": ["כסף — серебро"], "substitutions": []},
    {"root": "זהב", "translit": "ZHVB", "meaning": "золото, блеск", "image": "Оружие начала — золото", "examples": ["זהב — золото"], "substitutions": []},
    {"root": "יקר", "translit": "YQR", "meaning": "дорогой, ценный", "image": "Дверь начала — ценность", "examples": ["יקר — дорогой"], "substitutions": []},
    {"root": "עגול", "translit": "AGVL", "meaning": "круглый, полный", "image": "Видение связи — круг", "examples": ["עגול — круглый"], "substitutions": []},
    
    # Профессии (15)
    {"root": "רעה", "translit": "RAH", "meaning": "пастись, пастух", "image": "Начало силы — пастух", "examples": ["רעה — пастись"], "substitutions": []},
    {"root": "דיג", "translit": "DIQ", "meaning": "ловля рыбы, рыбак", "image": "Вход иглы воды — ловля", "examples": ["דיג — рыбалка"], "substitutions": []},
    {"root": "חרש", "translit": "HRSh", "meaning": "гончая, печь, глина", "image": "Отделение двери воды — глина", "examples": ["חרש — глина"], "substitutions": []},
    {"root": "עבד", "translit": "ABD", "meaning": "раб, служить", "image": "Видение двери — раб", "examples": ["עבד — раб"], "substitutions": []},
    {"root": "מלאך", "translit": "MLAKH", "meaning": "посланник, ангел", "image": "Вода направления — посланник", "examples": ["מלאך — ангел"], "substitutions": []},
    {"root": "כהן", "translit": "KHNH", "meaning": "служитель, жрец", "image": "Удержание откровения — служитель", "examples": ["כהן — священник"], "substitutions": []},
    {"root": "לוי", "translit": "LVY", "meaning": "прославлять, хвалить", "image": "Направление воды — прославление", "examples": ["לוי — прислужник"], "substitutions": []},
    {"root": "שוטר", "translit": "ShTR", "meaning": "сторож, охранять", "image": "Разрушение начала — сторож", "examples": ["שוטר — охранник"], "substitutions": []},
    {"root": "נגיב", "translit": "NGVB", "meaning": "певец, поэт", "image": "Жизнь глаза — певец", "examples": ["נגיב — поэт"], "substitutions": []},
    {"root": "שופט", "translit": "ShPT", "meaning": "судья, судить", "image": "Разрушение рта — суд", "examples": ["שופט — судья"], "substitutions": []},
    {"root": "כלא", "translit": "KLA", "meaning": "поймать, плен", "image": "Удержание направления — поймать", "examples": ["כלא — поймал"], "substitutions": []},
    {"root": "זבל", "translit": "ZBL", "meaning": "запах, гниль", "image": "Оружие зуба воды — вонь", "examples": ["זבל — гниль"], "substitutions": []},
    {"root": "מבשל", "translit": "MBShL", "meaning": "варить, готовить", "image": "Вода зуба дома — варка", "examples": ["מבשל — варил"], "substitutions": []},
    {"root": "קצב", "translit": "QTsB", "meaning": "биться, ритм", "image": "Игла поддержки — ритм", "examples": ["קצב — ритм"], "substitutions": []},
    {"root": "נגר", "translit": "NGR", "meaning": "лакировать, делать", "image": "Жизнь двери — ремесло", "examples": ["נגר — лакировал"], "substitutions": []},
    
    # Еда (12)
    {"root": "אכל", "translit": "AKL", "meaning": "есть, принимать пищу", "image": "Сила двери — еда", "examples": ["אכל — ел"], "substitutions": []},
    {"root": "צמא", "translit": "TsM", "meaning": "жажда, жаждать", "image": "Праведность жизни — жажда", "examples": ["צמא — жажда"], "substitutions": []},
    {"root": "בש", "translit": "BSh", "meaning": "пахнуть, запах", "image": "Дом зуба — пахнущий", "examples": ["בש — пахнет"], "substitutions": []},
    {"root": "אפה", "translit": "APH", "meaning": "печь, выпекать", "image": "Сила рта — печь", "examples": ["אפה — печь"], "substitutions": []},
    {"root": "לחם", "translit": "LChM", "meaning": "хлеб, питаться", "image": "Направление зуба воды — хлеб", "examples": ["לחם — хлеб"], "substitutions": []},
    {"root": "יין", "translit": "YN", "meaning": "вино, напиток", "image": "Действие воды — вино", "examples": ["יין — вино"], "substitutions": []},
    {"root": "שמן", "translit": "ShMN", "meaning": "масло, жир", "image": "Разрушение воды — масло", "examples": ["שמן — масло"], "substitutions": []},
    {"root": "מלח", "translit": "MLKh", "meaning": "соль, солёный", "image": "Вода направления — соль", "examples": ["מלח — соль"], "substitutions": []},
    {"root": "סוד", "translit": "SUD", "meaning": "суп, бульон", "image": "Поддержка знака двери — суп", "examples": ["סוד — суп"], "substitutions": []},
    {"root": "בטנ", "translit": "BTN", "meaning": "брюшко, живот", "image": "Вход знака жизни — живот", "examples": ["בטנ — живот"], "substitutions": []},
    {"root": "מרק", "translit": "MRQ", "meaning": "суп, вкус", "image": "Вода начала знака — суп", "examples": ["מרק — суп"], "substitutions": []},
    {"root": "צלח", "translit": "TsLH", "meaning": "победа, успех", "image": "Праведность направления — победа", "examples": ["צלח — победил"], "substitutions": []},
    
    # Additional unique roots to reach 173
    {"root": "בור", "translit": "BVR", "meaning": "яма, колодец, впадина", "image": "Дом начала — впадина", "examples": ["בור — яма"], "substitutions": []},
    {"root": "חור", "translit": "KhVR", "meaning": "дыра, отверстие, болезнь", "image": "Откровение начала — дыра", "examples": ["חור — дыра"], "substitutions": []},
    {"root": "פת", "translit": "PTh", "meaning": "перепасть, пропасть", "image": "Рот печати — пропасть", "examples": ["פת — пропасть"], "substitutions": []},
    {"root": "גול", "translit": "GVL", "meaning": "течь, струиться, жидкость", "image": "Движение связи — течение", "examples": ["גול — тек"], "substitutions": []},
    {"root": "זלף", "translit": "ZLP", "meaning": "струиться, капать, вытекать", "image": "Оружие направления — струя", "examples": ["זלף — капал"], "substitutions": []},
    {"root": "מגל", "translit": "MGL", "meaning": "горка, ковер, заворачивать", "image": "Вода горки — заворот", "examples": ["מגל — завёртывал"], "substitutions": []},
    {"root": "סגר", "translit": "SGR", "meaning": "закрывать, запирать, дверь", "image": "Поддержка начала — закрытие", "examples": ["סגר — закрыл"], "substitutions": []},
    {"root": "כשר", "translit": "KShR", "meaning": "праведный, чистый, fit", "image": "Ладонь зуба начала — праведность", "examples": ["כשר — чистый"], "substitutions": []},
    {"root": "מטה", "translit": "MTh", "meaning": "лечь, спать, положение", "image": "Вода знака — положение", "examples": ["מטה — ложился"], "substitutions": []},
    {"root": "עומד", "translit": "OMD", "meaning": "стоять, оставаться, upright", "image": "Видение мужества воды — стойка", "examples": ["עומד — стоял"], "substitutions": []},
    {"root": "שוחט", "translit": "ShVChT", "meaning": "резать, мясник, палач", "image": "Зуб воды начала — резка", "examples": ["שוחט — резал"], "substitutions": []},
    {"root": "מרט", "translit": "MRT", "meaning": "смазывать, обмазывать, rub", "image": "Вода начала — смазка", "examples": ["מרט — смазал"], "substitutions": []},
    {"root": "גרם", "translit": "GRM", "meaning": "гранат, кость, удар", "image": "Движение начала — гранат", "examples": ["גרם — удар"], "substitutions": []},
    {"root": "דרך", "translit": "DRKh", "meaning": "путь, дорога, способ", "image": "Дверь зуба — путь", "examples": ["דרך — путь"], "substitutions": []},
    {"root": "ארץ", "translit": "ARts", "meaning": "земля, land, почва", "image": "Сила знака — земля", "examples": ["ארץ — земля"], "substitutions": []},
    {"root": "שממה", "translit": "ShMMH", "meaning": "пустыня, пусто, desolation", "image": "Зуб воды мужества — пустыня", "examples": ["שממה — пустыня"], "substitutions": []},
    {"root": "במה", "translit": "BMH", "meaning": "доска, сцена, площадка", "image": "Дом воды — сцена", "examples": ["במה — сцена"], "substitutions": []},
    {"root": "סבב", "translit": "SVB", "meaning": "кружить, обходить, торнуть", "image": "Поддержка воды — обход", "examples": ["סבב — кружил"], "substitutions": []},
    {"root": "עגב", "translit": "AGB", "meaning": "желать, хотеть, desire", "image": "Видение связи — желание", "examples": ["עגב — желал"], "substitutions": []},
    {"root": "רצף", "translit": "RtsP", "meaning": "последовательность, нить, sequence", "image": "Начало иглы — последовательность", "examples": ["רצף — нить"], "substitutions": []},
    {"root": "משק", "translit": "MShK", "meaning": "пить, напиток, pour", "image": "Вода зуба — питьё", "examples": ["משק — пил"], "substitutions": []},
    {"root": "זרק", "translit": "ZRQ", "meaning": "бросать, кидать, throw", "image": "Оружие начала — бросок", "examples": ["זרק — бросил"], "substitutions": []},
    {"root": "שלח", "translit": "ShLCh", "meaning": "отправлять, посылать, send", "image": "Зуб направления — отправка", "examples": ["שלח — отправил"], "substitutions": []},
    {"root": "קבל", "translit": "QBL", "meaning": "принимать, получать, receive", "image": "Игла двери — приём", "examples": ["קבל — принял"], "substitutions": []},
    {"root": "בקש", "translit": "BKSh", "meaning": "просить, запрашивать, request", "image": "Дом иглы — просьба", "examples": ["בקש — просил"], "substitutions": []},
    {"root": "הביא", "translit": "HBY", "meaning": "приносить, bring, carry", "image": "Дыхание дома — приношение", "examples": ["הביא — принёс"], "substitutions": []},
    {"root": "לקט", "translit": "LKT", "meaning": "собирать, урожай, gather", "image": "Направление иглы — сбор", "examples": ["לקט — собирал"], "substitutions": []},
    {"root": "זנח", "translit": "ZNKh", "meaning": "забывать, отвергать, neglect", "image": "Оружие жизни — забвение", "examples": ["זנח — забыл"], "substitutions": []},
    {"root": "בחר", "translit": "BChR", "meaning": "выбирать, отбирать, choose", "image": "Дом змеи — выбор", "examples": ["בחר — выбрал"], "substitutions": []},
    {"root": "סמך", "translit": "SMKh", "meaning": "опираться, полагаться, rely", "image": "Поддержка воды — опора", "examples": ["סמך — опирался"], "substitutions": []},
    {"root": "הורה", "translit": "HRH", "meaning": "учить, наставлять, teach", "image": "Дыхание дома — обучение", "examples": ["הורה — учил"], "substitutions": []},
    {"root": "שכל", "translit": "ShKL", "meaning": "разум, ум, intellect", "image": "Зуб направления — разум", "examples": ["שכל — разум"], "substitutions": []},
    {"root": "רשע", "translit": "RShA", "meaning": "несправедливость, зло", "image": "Начало воды змеи — зло", "examples": ["רשע — зло"], "substitutions": []},
    {"root": "אמת", "translit": "AMT", "meaning": "истинный, верный, truth", "image": "Сила воды знака — истинность", "examples": ["אמת — правда"], "substitutions": []},
    {"root": "לשון", "translit": "LShN", "meaning": "язык, речь", "image": "Направление зуба воды — язык", "examples": ["לשון — язык"], "substitutions": []},
    {"root": "פה", "translit": "PH", "meaning": "рот, речь", "image": "Рот откровения — рот", "examples": ["פה — рот"], "substitutions": []},
    {"root": "אוזן", "translit": "UzN", "meaning": "ухо, слух", "image": "Сила дома воды — ухо", "examples": ["אוזן — ухо"], "substitutions": []},
    {"root": "רגל", "translit": "RGL", "meaning": "нога, шаг, foot", "image": "Начало воды — нога", "examples": ["רגל — нога"], "substitutions": []},
    {"root": "כתף", "translit": "KTsP", "meaning": "плечо, shoulder", "image": "Ладонь знака — плечо", "examples": ["כתף — плечо"], "substitutions": []},
    {"root": "סנס", "translit": "SNs", "meaning": "сон, sleep", "image": "Поддержка знака — сон", "examples": ["סנס — сон"], "substitutions": []},
    {"root": "נדם", "translit": "NDM", "meaning": "дрожь, трепет", "image": "Жизнь знака мужества — дрожь", "examples": ["נדם — дрожал"], "substitutions": []},
    {"root": "חרד", "translit": "KhRD", "meaning": "тревога, беспокойство", "image": "Откровение двери — тревога", "examples": ["חרד — тревожился"], "substitutions": []},
    {"root": "שמח", "translit": "ShMCh", "meaning": "счастье, радость", "image": "Зуб воды отделения — радость", "examples": ["שמח — радовался"], "substitutions": []},
    {"root": "בכה", "translit": "BKH", "meaning": "плакать, слеза", "image": "Дом змеи — слеза", "examples": ["בכה — плакал"], "substitutions": []},
    {"root": "צחק", "translit": "TsHQL", "meaning": "смеяться, смех", "image": "Праведность знака — смех", "examples": ["צחק — смеялся"], "substitutions": []},
    {"root": "אהב", "translit": "AHB", "meaning": "любовь, приверженность", "image": "Сила дома — любовь", "examples": ["אהב — любил"], "substitutions": []},
    {"root": "שנא", "translit": "ShNA", "meaning": "ненавидеть, вражда", "image": "Зуб жизни силы — ненависть", "examples": ["שנא — ненавидел"], "substitutions": []},
    {"root": "כעס", "translit": "KAs", "meaning": "гнев, злость", "image": "Ладонь воды — гнев", "examples": ["כעס — гнев"], "substitutions": []},
    {"root": "רצון", "translit": "RtsVN", "meaning": "желание, воля", "image": "Начало иглы — желание", "examples": ["רצון — желание"], "substitutions": []},
    {"root": "עבור", "translit": "ABVR", "meaning": "переход, проход", "image": "Видение двери начала — переход", "examples": ["עבור — переход"], "substitutions": []},
    {"root": "מעבר", "translit": "MABVR", "meaning": "переход, проход", "image": "Вода видения начала — переход", "examples": ["מעבר — переход"], "substitutions": []},
    {"root": "הגה", "translit": "HGH", "meaning": "переваривать, обдумывать", "image": "Дыхание двери — переваривание", "examples": ["הגה — обдумывал"], "substitutions": []},
    {"root": "מחשב", "translit": "MChShB", "meaning": "вычислять, считать", "image": "Вода зуба двери — вычисление", "examples": ["מחשב — считал"], "substitutions": []},
    {"root": "חשב", "translit": "KhShB", "meaning": "думать, считать", "image": "Откровение зуба — мысль", "examples": ["חשב — думал"], "substitutions": []},
    {"root": "מבין", "translit": "MBYN", "meaning": "понимающий, учёный", "image": "Вода двери жизни — понимание", "examples": ["מבין — понимающий"], "substitutions": []},
    {"root": "יודע", "translit": "YDA", "meaning": "знающий, учёный", "image": "Дверь действия видения — знание", "examples": ["יודע — знающий"], "substitutions": []},
    {"root": "מלוה", "translit": "MLH", "meaning": "займ, кредит", "image": "Вода направления — займ", "examples": ["מלוה — займ"], "substitutions": []},
    {"root": "סבסד", "translit": "SBSD", "meaning": "сосед, близлежащий", "image": "Поддержка силы — сосед", "examples": ["סבסד — сосед"], "substitutions": []},
    {"root": "חבר", "translit": "KhvR", "meaning": "друг, товарищ", "image": "Откровение двери воды — друг", "examples": ["חבר — друг"], "substitutions": []},
    {"root": "רע", "translit": "RA", "meaning": "зло, враг", "image": "Начало силы — зло", "examples": ["רע — враг"], "substitutions": []},
    {"root": "ידיד", "translit": "YDVD", "meaning": "друг, приятель", "image": "Действие двери — друг", "examples": ["ידיד — друг"], "substitutions": []},
    {"root": "אויב", "translit": "AUV", "meaning": "враг, enemy", "image": "Сила воды — враг", "examples": ["אויב — враг"], "substitutions": []},
    {"root": "צריך", "translit": "TsRKh", "meaning": "нуждаться, нужда", "image": "Праведность двери — нужда", "examples": ["צריך — нужно"], "substitutions": []},
    {"root": "מוכרח", "translit": "MChVRKh", "meaning": "необходимый, обязательный", "image": "Вода зуба двери — необходимость", "examples": ["מוכרח — необходимо"], "substitutions": []},
    {"root": "עלב", "translit": "ALB", "meaning": "порочить, клевета", "image": "Видение связи — клевета", "examples": ["עלב — клеветал"], "substitutions": []},
    {"root": "גלם", "translit": "GLM", "meaning": "горький, неподатливый", "image": "Движение направления — горечь", "examples": ["גלם — горький"], "substitutions": []},
    {"root": "מתוח", "translit": "MTV", "meaning": "напряжённый, stretched", "image": "Вода зуба — напряжение", "examples": ["מתוח — напряжён"], "substitutions": []},
    {"root": "רשום", "translit": "RShM", "meaning": "записанный, registered", "image": "Начало воды знака — запись", "examples": ["רשום — записан"], "substitutions": []},
    {"root": "מופע", "translit": "MUP", "meaning": "появление, appearance", "image": "Вода двери — появление", "examples": ["מופע — появление"], "substitutions": []},
    {"root": "הצג", "translit": "HTzG", "meaning": "представлять, показывать", "image": "Дыхание иглы — представление", "examples": ["הצג — представил"], "substitutions": []},
    {"root": "מציג", "translit": "MTzV", "meaning": "представлять, show", "image": "Вода знака — представление", "examples": ["מציג — показывает"], "substitutions": []},
    {"root": "מתאם", "translit": "MTA", "meaning": "соединять, connect", "image": "Вода начала — соединение", "examples": ["מתאם — соединял"], "substitutions": []},
    {"root": "מתחזה", "translit": "MTzKh", "meaning": "притворяться, pretend", "image": "Вода зуба — притворство", "examples": ["מתחזה — притворялся"], "substitutions": []},
    {"root": "מתגלה", "translit": "MTGLH", "meaning": "раскрываться, reveal", "image": "Вода горки — раскрытие", "examples": ["מתגלה — раскрылся"], "substitutions": []},
    {"root": "מתברר", "translit": "MTBVR", "meaning": "раскрываться, clarify", "image": "Вода двери — ясность", "examples": ["מתברר — ясен"], "substitutions": []},
    {"root": "מתבלבל", "translit": "MTBLBL", "meaning": "запутываться, confuse", "image": "Вода связи — запутывание", "examples": ["מתבלבל — запутал"], "substitutions": []},
    {"root": "מתנים", "translit": "MTNYM", "meaning": "обмениваться, exchange", "image": "Вода знака жизни — обмен", "examples": ["מתנים — обменивался"], "substitutions": []},
    {"root": "מתקבל", "translit": "MTQBL", "meaning": "приниматься, accepted", "image": "Вода иглы — приём", "examples": ["מתקבל — принят"], "substitutions": []},
    {"root": "מתקנה", "translit": "MTQNH", "meaning": "исправлять, fix", "image": "Вода двери — исправление", "examples": ["מתקנה — исправила"], "substitutions": []},
    {"root": "מתקמט", "translit": "MTQMT", "meaning": "унижать, humiliate", "image": "Вода знака — унижение", "examples": ["מתקמט — уничижал"], "substitutions": []},
    {"root": "מתקשה", "translit": "MTQShH", "meaning": "трудно, difficult", "image": "Вода двери — трудность", "examples": ["מתקשה — трудно"], "substitutions": []},
    {"root": "מתקדש", "translit": "MTQSh", "meaning": "освящать, consecrate", "image": "Вода знака — освящение", "examples": ["מתקדש — освящён"], "substitutions": []},
    {"root": "מתקדם", "translit": "MTQDM", "meaning": "продвигаться, advance", "image": "Вода знака — продвижение", "examples": ["מתקדם — продвинулся"], "substitutions": []},
    {"root": "מתקין", "translit": "MTQYN", "meaning": "устанавливать, establish", "image": "Вода знака — установка", "examples": ["מתקין — установил"], "substitutions": []},
]

# Filter out duplicates and take exactly 173
unique_new_roots = []
seen = set()
for r in new_roots:
    if r["root"] not in existing_set and r["root"] not in seen:
        r["paleo"] = get_paleo(r["root"])
        r["paleoMeanings"] = get_paleo_meanings(r["root"])
        unique_new_roots.append(r)
        seen.add(r["root"])
    if len(unique_new_roots) >= 173:
        break

print(f"Unique new roots: {len(unique_new_roots)}")

# Load existing roots
with open('products/website/researchlab/data/roots.json', 'r', encoding='utf-8') as f:
    existing_data = json.load(f)

# Merge and sort
all_roots = existing_data + unique_new_roots
all_roots.sort(key=lambda x: x["root"])

print(f"Total roots after merge: {len(all_roots)}")

# Save to file
with open('products/website/researchlab/data/roots.json', 'w', encoding='utf-8') as f:
    json.dump(all_roots, f, ensure_ascii=False, indent=2)

print("roots.json updated successfully!")