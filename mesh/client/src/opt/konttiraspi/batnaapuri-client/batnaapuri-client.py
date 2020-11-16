#!/usr/bin/env python3
'''Tämä on asiakas-esimerkki joka ottaa yhteyttä flaskin socket-palvelimelle'''
import subprocess, json, time, socketio, threading # sudo pip3 install python-socketio
from configobj import ConfigObj
config=ConfigObj('/boot/asetukset.txt')

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

class WsAsiakas:
    def __init__(self):
        self.socketOK=False
        self.t=threading.Thread(target=self.wsYhteys)
        self.t.start()
    def wsYhteys(self):
        self.sio=socketio.Client()
        while not self.socketOK:
            print("yhdistetään batnaapurit-serverille", flush=True)
            try:
                self.sio.connect(config.get("batnaapuri_server"),namespaces=['/meshraspi'])
            except socketio.exceptions.ConnectionError as err:
                print("ERR socketio ", err, flush=True)
                time.sleep(5)
            else:
                print("socketio conn ok", flush=True)
                self.socketOK=True
        @self.sio.on('connect_error')
        def connect_error(message):
            print('Connection was rejected due to ' + message, flush=True)

        @self.sio.on('newnumber', namespace='/meshraspi')
        def my_custom_event(data):
            print("---", data, flush=True)

    def laheta(self, sanoma):
        jsanoma=json.loads(sanoma)
        print("Lähettää", jsanoma, flush=True)
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
