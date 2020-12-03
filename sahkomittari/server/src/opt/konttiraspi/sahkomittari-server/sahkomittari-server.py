#!/usr/bin/env python3 
#

from websocket_server import WebsocketServer
from palveluws import PalveluWs #Websocket-palvelut
from datetime import datetime
import time, threading, logging, sys, os, json, logging, urllib.parse, sqlite3
DEBUG=False

kulutusTietokanta="/opt/konttiraspi/sahkomittari-server/data/kulutus.db"

viimTallennusaika="" #Tähän kirjoitetaan milloin pysyvät tiedostot on viimeksi tallennettu HH
kwhMuisti={} # {'fo-t-2332a': '0.45250'}
pulssiMuisti={} #lahettaja:pulssit
lampoMuisti={} #lahettaja:lämpötila
kosteusMuisti={} #lahettaja:kosteus

def tallennaPysyvat(): # Tallennetaan kulutuslukemat pysyvään paikalliseen tiedostoon
    aika=str(int(time.time())) #unix-aikaleima
    aika=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ulkolampo=-127.0 #haetaan tää lopullisessa versiossa tässä kohtaa serverin mittarilta?
    ulkokosteus=-127.0
    conn = sqlite3.connect(kulutusTietokanta)
    c = conn.cursor()
    for asiakasID in kwhMuisti: #käydään kaikki asiakkaa läpi yksi kerrallaan #TARKISTA TÄÄ OSUUS, LASKEE VÄÄRIN?
        kys=c.execute('SELECT kwh FROM kulutus WHERE id="'+asiakasID+'" ORDER BY aikaleima DESC LIMIT 1') #lasketaan ensin tunnin aikana tapahtunut kulutus vertaamalla nykyistä viimeksi tietokantaan tallennettuun lukemaan
        edtunti=None
        for i in kys:
            edtunti=str(i[0])
        if edtunti is None: #tietokannassa ei vielä ole kulutustietoa...
            edtunti=float(kwhMuisti[asiakasID]) #...joten kaikki kulutus on tälle tunnille
        tuntikohtainen=str(float(kwhMuisti[asiakasID])-float(edtunti))
        c.execute('INSERT into kulutus(aikaleima, id, kwh, pulssit, tuntikohtainen, lampo, kosteus, ulkolampo, ulkokosteus) VALUES("'+aika+'", "'+asiakasID+'", '+str(kwhMuisti[asiakasID])+', '+str(pulssiMuisti[asiakasID])+', '+str(tuntikohtainen)+', '+str(lampoMuisti[asiakasID])+', '+str(kosteusMuisti[asiakasID])+', '+str(ulkolampo)+', '+str(ulkokosteus)+')')
    conn.commit()
    conn.close()
#---------------------------------------------------------------------------------------------------------------------------------------------
def selainWscallback(client, server, data): #Internet-selaimella annetaan komentoja
    #ip = client["address"][0]
    jdata=json.loads(data)
    #print(jdata)
    if "komento" in jdata:
        kohdelaite=jdata["komento"]["laite"]
        tavu=jdata["komento"]["tavu"]
        relerivi='{"komento": {"laite": "'+kohdelaite+'", "tavu": "'+tavu+'"}}'
        mittariWs.lahetaYksityinen(kohdelaite, relerivi)

def mittariWscallback(client, server, data): #Raspberry lähettää mittarin lukemia
    #ip = client["address"][0]
    jsmessage=json.loads(data)
    #print(jsmessage, flush=True)
    if "raspilta" in jsmessage:
        lahettaja=next(iter(jsmessage['raspilta'].keys()))
        jsmessage=jsmessage["raspilta"][lahettaja]
        aika=datetime.now().strftime("%H:%M:%S")
        riviselaimille='{"elementit": ['
        riviselaimille+='{"elementti": "nahty_'+lahettaja+'", "arvo": "'+aika+'"}, '
        if "info" in jsmessage:
            info=jsmessage.get("info", "-")
            riviselaimille+='{"elementti": "info_'+lahettaja+'", "arvo": "'+info+'"}, '
        if "kwh" in jsmessage:
            kwhMuisti[lahettaja]=jsmessage["kwh"]
            riviselaimille+='{"elementti": "kwh_'+lahettaja+'", "arvo": "'+kwhMuisti[lahettaja]+'"}, '
        if "pulssit" in jsmessage:
            pulssiMuisti[lahettaja]=jsmessage.get("pulssit", "-")
            riviselaimille+='{"elementti": "pulssit_'+lahettaja+'", "arvo": "'+pulssiMuisti[lahettaja]+'"}, '
        if "reaaliaikainen" in jsmessage:
            reaaliaikainen=jsmessage.get("reaaliaikainen", "-")
            riviselaimille+='{"elementti": "reaali_'+lahettaja+'", "arvo": "'+reaaliaikainen+'"}, '
        if "lampo" in jsmessage:
            lampoMuisti[lahettaja]=jsmessage.get("lampo", "-")
            riviselaimille+='{"elementti": "lampo_'+lahettaja+'", "arvo": "'+lampoMuisti[lahettaja]+'"}, '
        if "kosteus" in jsmessage:
            kosteusMuisti[lahettaja]=jsmessage.get("kosteus", "-")
            riviselaimille+='{"elementti": "kosteus_'+lahettaja+'", "arvo": "'+kosteusMuisti[lahettaja]+'"}, '
        riviselaimille=riviselaimille[:-2] #viimeinen pilkku ja välilyönti pois
        riviselaimille+=']}'
        selainWs.lahetaKaikille(riviselaimille)

if __name__ == "__main__":    # PÄÄOHJELMA ALKAA

    selainWs=PalveluWs(8889, selainWscallback) #websocket-palvelin selaimille
    mittariWs=PalveluWs(8888, mittariWscallback) #websocket-palvelin mittari-raspeille

    conn = sqlite3.connect(kulutusTietokanta)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS kulutus (aikaleima DATE, id TEXT , kwh REAL, pulssit INTEGER, tuntikohtainen REAL, lampo REAL, kosteus REAL, ulkolampo REAL, ulkokosteus REAL)')
    conn.commit()
    conn.close()
    kierros=0
    while True: # PÄÄLOOPPI
        time.sleep(1)
        kello=time.strftime("%H")
        if kello != viimTallennusaika and kierros!=0: #Jos tunti on vaihtunut:
            tallennaPysyvat() #Tasatunnein tallennetaan lukemat tietokantaan pysyvästi
            viimTallennusaika=kello
        else:
            if kierros==0:               #jos on ohjelman ensimmäinen suorituskierros, mitään tallennettavaa ei vielä voi olla
                viimTallennusaika=kello
                #print("eka kierros")
        kierros+=1
