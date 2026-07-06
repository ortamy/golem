#!/usr/bin/env python3
"""
Заменяет эмодзи в заголовках H1 (# ) .md файлов на ![icon](путь/к/иконке.png)
в соответствии с правилами маппинга директорий.
"""

import os
import re
import sys

# Путь к корню проекта
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CONTENT_DIR = os.path.join(BASE_DIR, 'content')
ICONS_DIR = 'web/icons/32'

# Маппинг: относительный путь от content/ -> путь к иконке
# Важно: более специфичные пути должны быть раньше общих
PATH_TO_ICON = {
    'tanakh/books': f'{ICONS_DIR}/scrolls.png',
    'tanakh/persons': f'{ICONS_DIR}/person.png',
    'tanakh/events': f'{ICONS_DIR}/event.png',
    'bashah/books': f'{ICONS_DIR}/scrolls.png',
    'bashah/letters': f'{ICONS_DIR}/scales.png',
    'bashah/persons': f'{ICONS_DIR}/person.png',
    'bashah/events': f'{ICONS_DIR}/event.png',
    'bashah/teachings': f'{ICONS_DIR}/heart.png',
    'bashah/terminology': f'{ICONS_DIR}/scroll.png',
    'bashah/concepts': f'{ICONS_DIR}/anchor.png',
    'bashah/practices': f'{ICONS_DIR}/shield.png',
    'bashah/chronology': f'{ICONS_DIR}/hourglass.png',
    'bashah/manuscripts': f'{ICONS_DIR}/manuscripts.png',
    'bashah/geography': f'{ICONS_DIR}/geography.png',
    'bashah/nevua': f'{ICONS_DIR}/torch.png',
    'tzel/adam': f'{ICONS_DIR}/vase.png',
    'tzel/brit-nissuin': f'{ICONS_DIR}/ring.png',
    'tzel/elohim': f'{ICONS_DIR}/elohim.png',
    'tzel/hitgalut': f'{ICONS_DIR}/alert.png',
    'tzel/kehillah': f'{ICONS_DIR}/kehillah.png',
    'tzel/kelim': f'{ICONS_DIR}/hammer-and-chisel.png',
    'tzel/makom': f'{ICONS_DIR}/makom.png',
    'tzel/mikra': f'{ICONS_DIR}/mikra.png',
    'tzel/moadim': f'{ICONS_DIR}/track.png',
    'tzel/ruach': f'{ICONS_DIR}/ruach.png',
    'tzel/shedim': f'{ICONS_DIR}/shedim.png',
    'tzel/tamid': f'{ICONS_DIR}/tamid.png',
    'terminology': f'{ICONS_DIR}/scroll.png',
    'researches': f'{ICONS_DIR}/book.png',
    'teachings': f'{ICONS_DIR}/heart.png',
    'practices': f'{ICONS_DIR}/shield.png',
    'hebrew': f'{ICONS_DIR}/lamp.png',
    'exposed': f'{ICONS_DIR}/sword.png',
}

# Регулярка для поиска эмодзи (Unicode ranges для emoji)
# Покрывает большинство常见 emoji
EMOJI_RE = re.compile(
    '['
    '\U0001F300-\U0001F9FF'  # Misc symbols, emoticons, etc.
    '\U0001FA00-\U0001FA6F'  # Chess symbols
    '\U0001FA70-\U0001FAFF'  # Symbols extended-A
    '\U00002600-\U000027BF'  # Misc symbols
    '\U0000FE00-\U0000FE0F'  # Variation selectors
    '\U0000200D'             # Zero width joiner
    '\U00002702-\U000027B0'  # Dingbats
    '\U000024C2-\U0001F251'  # Enclosed characters
    ']+'
)

def get_icon_for_file(rel_path):
    """Определяет иконку для файла по его относительному пути."""
    # Нормализуем путь (убираем имя файла)
    dir_path = os.path.dirname(rel_path).replace('\\', '/')
    
    # Сортируем ключи по длине (более специфичные пути первыми)
    sorted_paths = sorted(PATH_TO_ICON.keys(), key=len, reverse=True)
    
    for path in sorted_paths:
        if dir_path.startswith(path):
            return PATH_TO_ICON[path]
    
    return None

def replace_emoji_in_line(line):
    """Заменяет первый эмодзи в строке на маркер для вставки иконки."""
    match = EMOJI_RE.search(line)
    if match:
        emoji = match.group(0)
        start, end = match.span()
        # Возвращаем строку без эмодзи и сам эмодзи
        return line[:start] + line[end:], emoji
    return line, None

def process_file(filepath):
    """Обрабатывает один .md файл."""
    rel_path = os.path.relpath(filepath, CONTENT_DIR).replace('\\', '/')
    icon = get_icon_for_file(rel_path)
    
    if not icon:
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    
    for line in lines:
        # Ищем строку, начинающуюся с "# " (H1 заголовок)
        if line.startswith('# '):
            # Проверяем, есть ли уже вставка иконки
            if '![icon](' not in line:
                stripped_line, emoji = replace_emoji_in_line(line)
                if emoji:
                    # Вставляем ![icon](путь) после "# " и перед остальным текстом
                    # "# эмодзи Текст" -> "# ![icon](путь) Текст"
                    # Нужно сохранить всё, что после эмодзи
                    new_line = f'# ![icon]({icon}) {stripped_line[2:].lstrip()}'
                    new_lines.append(new_line)
                    modified = True
                    continue
        
        new_lines.append(line)
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return (rel_path, icon)
    return None

def main():
    """Главная функция."""
    processed = 0
    modified = 0
    
    for root, dirs, files in os.walk(CONTENT_DIR):
        for filename in files:
            if not filename.endswith('.md'):
                continue
            
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, CONTENT_DIR).replace('\\', '/')
            processed += 1
            
            result = process_file(filepath)
            if result:
                rel, icon = result
                print(f'  [{icon}] {rel}')
                modified += 1
    
    print(f'\n{"="*50}')
    print(f'Всего .md файлов: {processed}')
    print(f'Обработано (заменены эмодзи): {modified}')
    print(f'Пропущено: {processed - modified}')

if __name__ == '__main__':
    main()