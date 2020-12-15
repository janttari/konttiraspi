#!/usr/bin/env python3
#
# Vastaanottaa videon, joka lähetetään tänne POSTilla
#
# sudo pip3 install aiohttp python-socketio
#
# lähetä curlilla video s.ts
# curl -F "soittolista=p.m3u8" -F "video=@s.ts" localhost:8080/video
#
#
# TODO: -kamera-client voisi lähettää videon keston, niin ei tartte siellä päässä keyframeja niin paljon
#       -sorttaa m3u8 tiedostot ennen lähetystä (vanhimmasta uusimpaan kun selain kääntää)

import datetime as dt
from aiohttp import web
import socketio
import asyncio
import json
import sys, os
from configobj import ConfigObj

config=ConfigObj('/boot/asetukset.txt')

sio = socketio.AsyncServer()
app = web.Application()
app._client_max_size=1024*1024*50 #max upitettavan tiedoston koko 50 megatavua
sio.attach(app)
skriptinHakemisto=os.path.dirname(os.path.realpath(__file__)) #Tämän skriptin fyysinen sijainti configia varten
wwwHakemisto = skriptinHakemisto+"/static" #tallennetaan tän hakemiston alle static-hakemistoon
os.makedirs(wwwHakemisto+"/hls", exist_ok=True)
selaimellelahetetyt=[] #selaimelle pushatut m3u8 (ettei lähetetä samaa useampaan kertaan (ts-sälää voi tulla useampi kerralla))
tslista={}#{m3u8A:[[ext0,ts0],[ext1,ts1]],m3u8B:[[ext0,ts0],[ext1,ts1]]}palvelimelle viimeisimmäät tulleet POSTit
#kamera-client POSTaa tänne videon
async def tulevaVideo(request):
    data = await request.post()
    video = data['video']
    soittolista = str(data['soittolista']) #m3u8-nimi
    extinf = str(data['extinf'])
    filename = video.filename #.ts nimi
    m3u8name = wwwHakemisto+"/hls/"+soittolista
    videofile = data['video'].file
    content = videofile.read()
    if not soittolista in selaimellelahetetyt: #tätä ei ole vielä pushattu selaimille
        selaimellelahetetyt.append(soittolista)
        if len(selaimellelahetetyt)>50: #pidetään vain rajallinen määrä lähetettyjä muistissa
            selaimellelahetetyt.pop(0)
        await lahetaYksittainen(soittolista)

    if soittolista not in tslista:
        tslista[soittolista]=[]
    tslista[soittolista].append([extinf,filename])
    if len(tslista)>50: # ei ole tarpeen säilyttää ikuisesti
        eka = next(iter(tslista)) #listan avaimet on YYMMDD-HHMMSS joten helppo löytää eka näin
        tslista.pop(eka)
    sortattulista=sorted(tslista[soittolista], key=lambda x:x[1]) #0001.ts lajitteluperuste
    with open(m3u8name,"w") as fsoittolista: #kirjoitetan itse soittolista. 
        fsoittolista.write("#EXTM3U\n#EXT-X-PLAYLIST-TYPE:VOD\n#EXT-X-TARGETDURATION:1\n#EXT-X-VERSION:4\n#EXT-X-MEDIA-SEQUENCE:0\n#EXT-X-DISCONTINUITY\n")
    with open("static/hls/"+filename,"wb") as tiedosto:
        tiedosto.write(content)
    with open(m3u8name,"a") as fsoittolista:
        for kohde in sortattulista:
            fsoittolista.write(kohde[0]+"\n"+kohde[1]+"\n") #ext inf \n .ts \n
    return web.Response(text="OK",content_type='text/html')

#anna selaimelle index.html
async def index(request):
    """Serve the client-side application."""
    print(request.query_string) #vois palauttaa mobiilin, jos mobiili
    if "mobiili" in request.query_string.lower():
        print("MOBIILIHOMO")
        with open('static/mobile.html') as f:
            return web.Response(text=f.read(), content_type='text/html')
    with open('static/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

#uusi liiketapahtuma, lähetetään se kaikille selaimille
async def lahetaYksittainen(slista):
    video={"videoname":"* "+slista, "videouri": "/static/hls/"+slista}
    await sio.emit('videopush', video, namespace='/selaindata')

#lähetetään selaimelle sen pyytämä filtteröity videolista
async def lahetaFiltteroidyt(pyytaja, camnimi, aikayksikko, aikanum):
    hlshak=wwwHakemisto+"/hls/"
    now = dt.datetime.now()
    if aikayksikko == "tunti":
        ago = now-dt.timedelta(hours=aikanum)
    if aikayksikko == "paiva":
        ago = now-dt.timedelta(days=aikanum)
    elif aikayksikko == "viikko":
        ago = now-dt.timedelta(weeks=aikanum)
    videolista=[]
    for root, dirs,files in os.walk(hlshak):  
        files.sort()
        for fname in files:
            path = os.path.join(root, fname)
            st = os.stat(path)    
            mtime = dt.datetime.fromtimestamp(st.st_mtime)
            if mtime > ago:
                alku, paate= os.path.splitext(fname)
                if paate==".m3u8" and camnimi.lower() in alku.lower():
                    #print('%s modified %s'%(path, mtime))
                    videolista.append({"videoname":alku, "videouri": "/static/hls/"+fname})
    await sio.emit('videolista', videolista, namespace='/selaindata', room=pyytaja)

#selain pyytää filtteröityä tallennelistaa
@sio.on('selainfiltteri', namespace='/selaindata') 
async def message(sid, data):
    camnimi=data["camnimi"]
    aikayksikko=data["aikayksikko"]
    aikanum=float(data["aikanum"])
    await lahetaFiltteroidyt(sid, camnimi, aikayksikko, aikanum)

# uusi selain on liittynyt, lähetetään sille päivän videolista
@sio.event(namespace='/selaindata')
async def connect(sid, environ):
    await lahetaFiltteroidyt(sid, "", "paiva", 1)

app.router.add_static('/static', 'static') #staattiset tiedostot tässä hakemistossa
app.router.add_post("/video", tulevaVideo) #kamera-client postaa dataa tänne
app.router.add_get('/', index) #selaimelle index.html

#taustalla pyörivä looppi, johon voidaan lisätä määräajoin tehtäviä toimia
async def tausta(app):
    await asyncio.sleep(2)
    sys.stdout = sys.__stdout__ #palauta tulostusmahdollisuus
    while True:
        await asyncio.sleep(5)

#luo tarvittavat tausta tehtävät
async def start_background_tasks(app):
    pass
    app['tausta'] = asyncio.create_task(tausta(app))

if __name__ == '__main__':
    app.on_startup.append(start_background_tasks)
    sys.stdout = open(os.devnull, 'w') #estä tulostus (piilottaa aiohttp:n running-viestin)
    web.run_app(app, port=int(config.get('cam_serverport')),)
