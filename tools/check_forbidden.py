import json

with open('products/website/apps/researchlab/data/roots/roots.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

forbidden = ['вера', 'истина', 'святость', 'спасение', 'душа', 'дух', 'грех', 'благодать', 'закон', 'завет', 'церковь']
found = [r for r in data if any(f in r['meaning'].lower() for f in forbidden)]

print('Roots with forbidden words:', len(found))
for r in found:
    print(f'{r["root"]}: {r["meaning"]}')