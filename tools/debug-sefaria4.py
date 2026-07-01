#!/usr/bin/env python3
import urllib.request, json, ssl, re
from pathlib import Path

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request('https://www.sefaria.org/api/v3/texts/Genesis%201', headers={'User-Agent':'Golem/1.0'})
resp = urllib.request.urlopen(req, timeout=30, context=ctx)
data = json.loads(resp.read().decode('utf-8'))

versions = data.get('versions', [])
hebrew_verses = []
for version in versions:
    if not isinstance(version, dict):
        continue
    lang = version.get('language', '')
    text = version.get('text', [])
    if lang == 'he' and isinstance(text, list):
        hebrew_verses = [re.sub(r'<[^>]+>', '', str(t)) if t else "" for t in text]

print(f'hebrew_verses count: {len(hebrew_verses)}')
print(f'First verse: {repr(hebrew_verses[0][:100])}')
print(f'Last verse: {repr(hebrew_verses[-1][:100])}')

# Now simulate the verse building loop
niqqud_chars = set(range(0x0591, 0x05C8))
verses = []
for i, hebrew_verse in enumerate(hebrew_verses):
    hebrew_verse = hebrew_verse.strip()
    print(f'[{i}] stripped length: {len(hebrew_verse)}, empty: {not hebrew_verse}')
    if not hebrew_verse:
        continue
    hebrew_plain = "".join(ch for ch in hebrew_verse if ord(ch) not in niqqud_chars)
    hebrew_plain = " ".join(hebrew_plain.split())
    verses.append({"verse": i+1, "hebrew": hebrew_verse[:50], "plain_len": len(hebrew_plain)})
    if i < 3:
        print(f'  -> Added verse {i+1}')

print(f'\nTotal verses built: {len(verses)}')