#!/usr/bin/env python3
import json
v = json.load(open('products/website/apps/researchlab/data/scripture/bereshit-1.json', encoding='utf-8'))
for i in range(5):
    print(f'{v[i]["chapter"]}:{v[i]["verse"]} hebrew={v[i].get("hebrew","")[:50]} paleo={v[i].get("paleo","")[:25]}')