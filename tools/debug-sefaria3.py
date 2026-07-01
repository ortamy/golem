#!/usr/bin/env python3
import urllib.request, json, ssl, re
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request('https://www.sefaria.org/api/v3/texts/Genesis%201', headers={'User-Agent':'Golem/1.0'})
resp = urllib.request.urlopen(req, timeout=30, context=ctx)
data = json.loads(resp.read().decode('utf-8'))
versions = data.get('versions', [])
for version in versions:
    if not isinstance(version, dict):
        continue
    lang = version.get('language', '')
    text = version.get('text', [])
    if lang == 'he' and isinstance(text, list):
        print(f'Total items in text array: {len(text)}')
        print(f'Non-empty items: {sum(1 for t in text if str(t).strip())}')
        print('\nAll non-empty verses:')
        for i, t in enumerate(text):
            cleaned = re.sub(r'<[^>]+>', '', str(t)) if t else ""
            if cleaned.strip():
                print(f'  [{i}] {repr(cleaned[:80])}')