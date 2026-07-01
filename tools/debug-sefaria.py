#!/usr/bin/env python3
import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request('https://www.sefaria.org/api/v3/texts/Genesis%201', headers={'User-Agent':'Golem/1.0'})
resp = urllib.request.urlopen(req, timeout=30, context=ctx)
data = json.loads(resp.read().decode('utf-8'))
print('Top keys:', list(data.keys()))
print('versions type:', type(data.get('versions')))
if isinstance(data.get('versions'), list):
    print('versions len:', len(data['versions']))
    for i, v in enumerate(data['versions'][:3]):
        print(f'version[{i}] keys:', list(v.keys()) if isinstance(v, dict) else type(v))
        if isinstance(v, dict):
            print(f'  language:', v.get('language'))
            print(f'  text type:', type(v.get('text')))
            print(f'  text len:', len(v.get('text',[])) if isinstance(v.get('text'), list) else 'N/A')
            if isinstance(v.get('text'), list) and v.get('text'):
                print(f'  first text item:', repr(v['text'][0])[:200])