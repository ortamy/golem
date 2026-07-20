import re
path = r'products/website/apps/researchlab/index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

categories = {
    'Исследователь': 'Исследователь',
    'Разоблачатель': 'Исследователь',
    'Сборщик': 'Исследователь',
    'Семитолог': 'Исследователь',
    'Компаратор': 'Исследователь',
    'Переводчик палео-иврита': 'Исследователь',
    'Фронтенд-разработчик': 'Разработчик',
    'AI-инженер': 'Разработчик',
    'Критик': 'Контроль',
    'Проверяющий': 'Контроль',
    'Ревьюер кода': 'Контроль',
    'Редактор': 'Документация',
    'Технический писатель': 'Документация',
    'Архитектор потока': 'Оркестрация',
    'Связной': 'Оркестрация',
}

start_marker = "aiAgents: function()"
end_marker = "edChat: function()"
start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)
if start_idx == -1 or end_idx == -1:
    print('ERROR: could not find aiAgents section')
    exit(1)

section = content[start_idx:end_idx]
modified_section = section

for agent_name, category in categories.items():
    card_start = modified_section.find(f'alt="{agent_name}"')
    if card_start == -1:
        print(f'WARNING: card for "{agent_name}" not found')
        continue
    card_end = modified_section.find('</div>', card_start)
    if card_end == -1:
        print(f'WARNING: closing div for "{agent_name}" not found')
        continue
    badge_check = modified_section.find('agent-badge', card_start, card_end + 20)
    if badge_check != -1:
        print(f'SKIP: "{agent_name}" already has badge')
        continue
    badge_html = f'<span class="agent-badge">{category}</span>'
    modified_section = modified_section[:card_end] + badge_html + modified_section[card_end:]
    print(f'ADDED badge "{category}" to "{agent_name}"')

badge_count = modified_section.count('agent-badge')
print(f'Total badges in aiAgents section: {badge_count}')

content = content[:start_idx] + modified_section + content[end_idx:]
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('File saved successfully')
