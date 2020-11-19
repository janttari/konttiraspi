#!/usr/bin/env python3
'''Tämä on asiakas-esimerkki joka ottaa yhteyttä flaskin socket-palvelimelle'''
import subprocess, json, time, datetime, threading, websocket
from configobj import ConfigObj
config=ConfigObj('/boot/asetukset.txt')

def lokita(data, flush=True):
    with open("/home/pi/batloki", "a") as kirj:
        aika=str(datetime.datetime.now())
        kirj.write(aika+" "+data+"\n")
        print(aika+" "+data, flush=flush)

def kyseleNaapurit(): #kyselee batmanin näkemät naapurilaitteet # [('00:c0:ca:98:8f:9f', ' 0.500', ' 7.8'), ('00:c0:ca:98:8e:ed', ' 0.190', '35.6')]
    tamaLaiteMAC = subprocess.getoutput('sudo batctl n|grep -o "MAC:.*"|cut -d "/" -f2|cut -d " " -f1')
    tamaLaiteIP = subprocess.getoutput('ifconfig |grep bat0 -A1|tail -n 1|grep -o "inet.*" | cut -d " " -f 2') #vittu mitä paskaa, fiksaa tää :D
    naapuritraaka = subprocess.getoutput('sudo batctl n -H').split("\n")
    jrivi='{"laite": "'+config.get("mesh_name")+'", "mac": "'+tamaLaiteMAC+'", "ip": "'+tamaLaiteIP+'", "data": ['
    for n in naapuritraaka:
        nmac = n[0:17]
        nviive = n[19:26]
        nteho = n[36:40]
        if len(nmac)>0:
            jrivi+='{"mac": "'+nmac+'", "viive": "'+nviive+'", "teho": "'+nteho+'"},'
    if jrivi [-1] != '[':
        jrivi=jrivi[:-1]
    jrivi=jrivi+']}'
    #print(jrivi)
    return jrivi

class WsAsiakas(): #-----------------------------------------------------------------------------------------------------
    def __init__(self):
        self.socketok=False
        self.palvelin=config.get('batnaapuri_server')
        self.t=threading.Thread(target=self.wsYhteys)
        self.t.start()

    def wsYhteys(self):
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(self.palvelin,
                                  on_message = self.on_message,
                                  on_error = self.on_error,
                                  on_close = self.on_close,
                                  on_open = self.on_open)
        self.ws.run_forever()

    def on_message(self, message):
        lokita("MSG "+str(message))
        pass

    def on_error(self, error):
        self.socketok=False
        lokita("SOCK ERR "+str(error), flush=True)
        pass

    def on_close(self, ws):
        lokita("CLOSE", flush=True)

    def on_open(self):
        self.socketok=True
        lokita("SOCK OPEN", flush=True)
        pass

    def lahetaWs(self, sanoma):
        jsanoma=json.loads(sanoma)
        lokita("LAHETA", flush=True)
        try:
            self.ws.send(sanoma)
        except: #jos lähetys ei onnistu
            lokita("ERR send", flush=True)
            self.socketok=False
            self.reconnect() #Pyydetään avaamaan ws uudelleen

    def reconnect(self): #avaa ws uudelleen
        lokita("SOCKET RECONN", flush=True)
        self.t.join()
        time.sleep(10)
        self.t=threading.Thread(target=self.wsYhteys)
        self.t.start()
#------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    wsAsiakas=WsAsiakas()
    k=0
    while True:
        k+=1
        if k%10 == 0: #muuta tämä hakemaan configista. 60 sek vois olla ok
            naap=kyseleNaapurit()
            wsAsiakas.lahetaWs(naap)
        time.sleep(1)
