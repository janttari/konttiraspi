#!/usr/bin/env python3
'''Tämä on asiakas-esimerkki joka ottaa yhteyttä flaskin socket-palvelimelle'''
import subprocess, json, time, socketio, threading # sudo pip3 install python-socketio
from configobj import ConfigObj
config=ConfigObj('/boot/asetukset.txt')
sio=socketio.Client()
socketOK=False

def kyseleNaapurit(): #kyselee batmanin näkemät naapurilaitteet # [('00:c0:ca:98:8f:9f', ' 0.500', ' 7.8'), ('00:c0:ca:98:8e:ed', ' 0.190', '35.6')]
    tamaLaiteMAC = subprocess.getoutput('sudo batctl n|grep -o "MAC:.*"|cut -d "/" -f2|cut -d " " -f1')
    tamaLaiteIP = subprocess.getoutput('ifconfig |grep bat0 -A1|tail -n 1|grep -o "inet.*" | cut -d " " -f 2') #vittu mitä paskaa, fiksaa tää :D
    naapuritraaka = subprocess.getoutput('sudo batctl n -H').split("\n")
    jrivi='{"laite": "'+config.get("mesh_name")+'", "mac": "'+tamaLaiteMAC+'", "ip": "'+tamaLaiteIP+'", "data":  ['
    for n in naapuritraaka:
        nmac = n[0:17]
        nviive = n[19:26]
        nteho = n[36:40]
        if len(nmac)>0:
            jrivi+='{"mac": "'+nmac+'", "viive": "'+nviive+'", "teho": "'+nteho+'"},'
    if jrivi [:-1] != '[':
        jrivi=jrivi[:-1]
    jrivi=jrivi+']}'
    #print(jrivi)
    return jrivi

class WsAsiakas():
    def __init__(self):
        self.yhteys=threading.Thread(target=self.wsyhteys)
        self.yhteys.start()

    def wsyhteys(self):
        while True:
            self.yhdista()

    def yhdista(self):
        global socketOK
        while not socketOK:
            print("yhdistetaan bat-serverille", flush=True)
            try:
                sio.connect(config.get("batnaapuri_server"),namespaces=['/meshraspi'])
            except:
                print("yhdistäminen ei onnistunut, odotetaan hetki", flush=True)
                time.sleep(5)
            else:
                socketOK=True


    def katkaise(self):
        global socketOK
        print("Katkaise", flush=True)
        socketOK=False
        sio.disconnect()
        time.sleep(5)
        print("uudelleenyhd", flush=True)
        self.yhdista()


    def laheta(self, sanoma):
        global socketOK
        jsanoma=json.loads(sanoma)
        if socketOK:
            #print("Lähettää", jsanoma, flush=True)
            try:
                sio.emit('naapuri_message', sanoma, namespace='/meshraspi')
            except:
                katkaise()
        else:
            print("ei voi lähettää, ei yhteyttä", flush=True)


@sio.event
def connect():
    print('connected!', flush=True)

@sio.event
def disconnect():
    global socketOK
    w.katkaise()

if __name__ == "__main__":
    w=WsAsiakas()
    k=0
    while True:
        k+=1
        if k%30 == 0 or k== 2: #muuta tämä hakemaan configista. 60 sek vois olla ok
            naap=kyseleNaapurit()
            w.laheta(naap)
        time.sleep(1)
