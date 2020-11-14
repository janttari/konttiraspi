#!/usr/bin/env python3
'''Tämä on asiakas-esimerkki joka ottaa yhteyttä flaskin socket-palvelimelle'''
import subprocess, json, time, socketio, threading # sudo pip3 install python-socketio
from configobj import ConfigObj
config=ConfigObj('/boot/asetukset.txt')

def kyseleNaapurit(): #kyselee batmanin näkemät naapurilaitteet # [('00:c0:ca:98:8f:9f', ' 0.500', ' 7.8'), ('00:c0:ca:98:8e:ed', ' 0.190', '35.6')]
    tamaLaiteMAC = subprocess.getoutput('sudo batctl n|grep -o "MAC:.*"|cut -d "/" -f2|cut -d " " -f1')
    naapuritraaka = subprocess.getoutput('sudo batctl n -H').split("\n")
    jrivi='{"laite": "'+config.get("mesh_name")+'", "mac": "'+tamaLaiteMAC+'", "data":  ['
    for n in naapuritraaka:
        nmac = n[0:17]
        nviive = n[20:26]
        nteho = n[36:40]
        jrivi+='{"mac": "'+nmac+'", "viive": "'+nviive+'", "teho": "'+nteho+'"},'
    jrivi=jrivi[:-1]+']}'
    return jrivi

class WsAsiakas:
    def __init__(self):
        self.socketOK=False
        self.t=threading.Thread(target=self.wsYhteys)
        self.t.start()
    def wsYhteys(self):
        while not self.socketOK:
            print("yhdistetään batnaapurit-serverille")
            try:
                self.sio=socketio.Client()
                self.sio.connect(config.get("batnaapuri_server"),namespaces=['/meshraspi'])
                self.socketOK=True
            except:
                print("ERR socketio")
                self.socketOK=False
                time.sleep(5)
        @self.sio.on('connect_error')
        def connect_error(message):
            print('Connection was rejected due to ' + message)

        @self.sio.on('newnumber', namespace='/meshraspi')
        def my_custom_event(data):
            print("---", data)

    def laheta(self, sanoma):
        jsanoma=json.loads(sanoma)
        self.sio.emit('naapuri_message', sanoma, namespace='/meshraspi')

if __name__ == "__main__":
    a=WsAsiakas()
    k=0
    while True:
        k+=1
        if k%10 == 0 or k== 2: #muuta tämä hakemaan configista. 60 sek vois olla ok
            naap=kyseleNaapurit()
            a.laheta(naap)
        time.sleep(1)
