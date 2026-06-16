#!/usr/bin/env python
# -*- coding: utf-8 -*-

def gen():
    import base64
    lines = []
    lines.append("# " + chr(0x1f6d0) + " Шаббат \u2014 שַבָּת \u2014 Суббота покоя")
    lines.append("")
    lines.append("**Метаданные файла**")
    lines.append("- **Файл:** `content/practices/shabbat.md`")
    lines.append("- **Версия:** 2.0")
    b64 = base64.b64encode(('\n'.join(lines)).encode('utf-8'))
    return b64

b64 = gen()
with open("b64output.txt","wb") as f:
    f.write(b64)
print("Generated: ", len(b64), "base64 chars")
