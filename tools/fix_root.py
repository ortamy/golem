import json

with open('products/website/researchlab/data/roots.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Fix the root "רוח" - remove "дух" from meaning
for r in data:
    if r['root'] == 'רוח':
        r['meaning'] = 'ветер, дуновение'
        print(f'Fixed: {r["root"]} - {r["meaning"]}')

with open('products/website/researchlab/data/roots.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('File updated successfully!')