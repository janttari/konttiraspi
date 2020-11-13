#!/usr/bin/env python3
'''Tämä on asiakas-esimerkki joka ottaa yhteyttä flaskin socket-palvelimelle'''
import subprocess, json, time, socketio, threading # sudo pip3 install python-socketio
from configobj import ConfigObj

config=ConfigObj('/boot/asetukset.txt')

def kyseleNaapurit(): #kyselee batmanin näkemät naapurilaitteet # [('00:c0:ca:98:8f:9f', ' 0.500', ' 7.8'), ('00:c0:ca:98:8e:ed', ' 0.190', '35.6')]
    #print("OMA IP: "+omaIP, omaMAC)
    naapuritraaka = subprocess.getoutput('sudo batctl n -H').split("\n")
    print(naapuritraaka)
    tmpnaapurit=[]
    ##
    #jrivi='{"laite": "'+config.get("mesh_name")+'", "data":  ['
    #tmpnaapurit = [('00:c0:ca:98:8f:9f', ' 0.500', ' 7.8'), ('00:c0:ca:98:8e:ed', ' 0.190', '35.6')] #DEMO
    #for t in tmpnaapurit:
    #    nmac=t[0]
    #    nviive=t[1]
    #    nteho=t[2]
    #    jrivi+='{"mac": "'+nmac+'", "viive": "'+nviive+'", "teho": "'+nteho+'"},'
    #jrivi=jrivi[:-1]+']}'
    #print("JJJJJJJJ", jrivi)
    ##
    #return jrivi
    jrivi='{"laite": "'+config.get("mesh_name")+'", "data":  ['
    for n in naapuritraaka:
        nmac = n[0:17]
        nviive = n[20:26]
        nteho = n[36:40]
        #print(nmac,naika,nteho)
        jrivi+='{"mac": "'+nmac+'", "viive": "'+nviive+'", "teho": "'+nteho+'"},'
    jrivi=jrivi[:-1]+']}'
    print("JJJJJJJJ", jrivi)
    #tmpnaapurit.append((nmac,naika,nteho))
    return jrivi
    #return tmpnaapurit # [('00:c0:ca:98:8f:9f', ' 0.500', ' 7.8'), ('00:c0:ca:98:8e:ed', ' 0.190', '35.6')]

class WsAsiakas:
    def __init__(self):
        self.t=threading.Thread(target=self.wsYhteys)
        self.t.start()
    def wsYhteys(self):
        self.sio=socketio.Client()
        self.sio.connect(config.get("batnaapuri_server"),namespaces=['/meshraspi'])
        @self.sio.on('newnumber', namespace='/meshraspi')
        def my_custom_event(data):
            print("---", data)
    def laheta(self, sanoma):
        jsanoma=json.loads(sanoma)
        print(jsanoma)
        self.sio.emit('naapuri_message', sanoma, namespace='/meshraspi')

if __name__ == "__main__":
    a=WsAsiakas()
    k=0
    while True:
        k+=1
        print(k)
        if k%10 == 0 or k== 2:
            naap=kyseleNaapurit()
            #print(naap)
            a.laheta(naap)
        #if k%13 == 0:
        #    print("muutos")
        #    a.laheta('{"laite": "'+config.get("mesh_name")+'", "data": [{"mac": "00:c0:ca:98:8f:9f", "viive": " 1.500", "teho": " 7.8"}, {"mac": "00:c0:ca:98:8e:ed", "viive": " 0.190", "teho": "35.6"}, {"mac": "00:c0:ca:98:8e:31", "viive": " 0.190", "teho": "22.6"}]}')
        #a.laheta('{"data": "piip"}')
        time.sleep(1)
