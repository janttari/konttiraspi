#!/usr/bin/env python3
from websocket_server import WebsocketServer
from palveluws import PalveluWs #Websocket-palvelut
from datetime import datetime
import time, sys, os, json #, logging, threading,logging, urllib.parse
from configobj import ConfigObj
import networkx as nx #emuloi kontti-raspberryjen MESH-verkkoa jossa raspit raportoi naapuri laitteistaan tälle serverille
import matplotlib.pyplot as plt
#DEBUG=False

config=ConfigObj('/boot/asetukset.txt')
skriptinHakemisto=os.path.dirname(os.path.realpath(__file__))
#DATAT:
meshnaapuridata={} #tässä on clientien ilmoittamien naapurihavaintojen kokonaisuus
viimmeshnaapuridata={} #tässä on clientien ilmoittamien naapurihavaintojen kokonaisuus viimeinnen tunnettu tila vertailua varten
MNT={} #Mac --> Nimi
MIP={} #MAC --> IP

havaintoaika={} #MAC aikaleima Laitenähty viimeksi

def luoVisuaali():
    G = nx.Graph()
    #print("luovisuaali", meshnaapuridata, flush=True)
    for isan in meshnaapuridata: #käydään isäntien naapurit läpi
        if isan in MNT:
            isannimi=MNT[isan][-6:]
        else:
            isannimi=isan[-5:]
        for naap in meshnaapuridata[isan]["naapurit"]:
            naapuri=naap["laite"]
            if naapuri in MNT:
                naapurinimi=MNT[naapuri][-6:]
            else:
                naapurinimi=naapuri[-5:]
            #if naapuri=='':
            #    break
            teho=naap["teho"]
            #print(teho)
            G.add_edge(isannimi, naapurinimi, valimatka=int(40-float(teho)))
    pos = nx.spring_layout(G, seed=0)
    plt.figure(figsize=(9, 9))
    nx.draw(G, pos,with_labels = True, node_color ='blue', node_size=3000, font_size=8, font_color="yellow")
    edge_labels = nx.get_edge_attributes(G,'valimatka')
    nx.draw_networkx_edge_labels(G, pos, edge_labels = edge_labels)
    plt.savefig('/www/batnaapurit/kartta.png')
    #plt.clf()
    #plt.cla()
    plt.close()
    selainWs.lahetaKaikille("paivitakuva")
    #self.socketio.emit('paivitakuva', {'data': 0}, namespace='/selain') #kaikille namespacessa

def vertaaNaapuriMuutoksia(): #onko naapuridatassa tapahtunut muutoksia?
    global viimmeshnaapuridata
    muuttunut=False
    for isanta in meshnaapuridata:
        for naapurit in meshnaapuridata[isanta]["naapurit"]:
            if isanta in viimmeshnaapuridata:
                vanhat=viimmeshnaapuridata[isanta]["naapurit"]
                if meshnaapuridata[isanta]["naapurit"] != vanhat:
                    muuttunut=True
            else:
                muuttunut=True
    if muuttunut:
        viimmeshnaapuridata=meshnaapuridata.copy()
        luoVisuaali()

def tarkistaKadonneet(): # käydään läpi laitteiden viimeiset havaintoajat
    for laite in list(MNT):
        nahtyViimeksi=time.time()-havaintoaika[laite]
        if nahtyViimeksi >=180: # yli kolme minuttia näkemisestä
            #print("kadonnut", laite)
            del meshnaapuridata[laite]
            del MNT[laite]
            luoVisuaali()
        #print("MNT: ",laite, havaintoaika[laite])

def selainWscallback(client, server, data): #Internet-selaimella annetaan komentoja
    pass

def batWscallback(client, server, data): #Raspberry lähettää batnaapureita
    print(data)
    jdata=json.loads(data)
    print(jdata)
    isantaNimi=jdata["laite"]
    isantaIP=jdata["ip"]
    isantaMAC=jdata["mac"]
    MNT[isantaMAC]=isantaNimi #päivitetään nimet
    MIP[isantaMAC]=isantaIP
    havaintoaika[isantaMAC]=time.time()
    naap=[]
    for j in jdata["data"]:
        nmac=j["mac"]
        nteho=j["teho"]
        nviive=j["viive"]
        kohde={"laite": nmac, "teho": nteho, "viive": nviive}
        naap.append(kohde)
    meshnaapuridata[isantaMAC]={"naapurit": naap}
    vertaaNaapuriMuutoksia()

if __name__ == '__main__':
    selainWs=PalveluWs(8090, selainWscallback) #websocket-palvelin selaimille
    batWs=PalveluWs(int(config.get("batnaapuri_portti")), batWscallback) #websocket-palvelin raspien batnaapureille
    num=0
    while True:
        num+=1
        if num % 10 == 0:
            tarkistaKadonneet()
        #f.lahetaSelain("piip"+str(num))
        time.sleep(1)
