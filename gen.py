import base64  
import sys  
data = base64.b64decode(  
open('b64content.txt','rb').read()  
)  
with open('content/practices/shabbat.md','wb') as f:  
    f.write(data)  
print('Done:', len(data), 'bytes') 
