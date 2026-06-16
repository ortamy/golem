#!python
import base64, os
f=open("b64data.txt","rb")
d=base64.b64decode(f.read())
f.close()
open("content/practices/yom-truah.md","wb").write(d)
print("OK")
