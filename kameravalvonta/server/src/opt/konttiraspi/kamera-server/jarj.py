#!/usr/bin/env python3
import os
import datetime as dt
camnimi=""
videolista=[]	
hlshak="static/hls/"
now = dt.datetime.now()
ago = now-dt.timedelta(days=1)
for root, dirs,files in os.walk(hlshak):  
        print("----")
        files.sort()
        for fname in files:
            path = os.path.join(root, fname)
            st = os.stat(path)    
            mtime = dt.datetime.fromtimestamp(st.st_mtime)
            if mtime > ago:
                alku, paate= os.path.splitext(fname)
                if paate==".m3u8" and camnimi.lower() in alku.lower():
                    print('%s modified %s'%(path, mtime))
                    videolista.append({"videoname":alku[:-1], "videouri": "/static/hls/"+fname})
    #Sorttaa videot tässä vanhimmasta uusimpaan!
    #await sio.emit('videolista', videolista, namespace='/selaindata', room=pyytaja)

