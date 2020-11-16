#!/usr/bin/env python3
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, request
import time, threading, logging, sys, matplotlib, json
import networkx as nx #emuloi kontti-raspberryjen MESH-verkkoa jossa raspit raportoi naapuri laitteistaan tälle serverille
import matplotlib.pyplot as plt
from configobj import ConfigObj

config=ConfigObj('/boot/asetukset.txt')

meshnaapuridata={} #tässä on clientien ilmoittamien naapurihavaintojen kokonaisuus
viimmeshnaapuridata={} #tässä on clientien ilmoittamien naapurihavaintojen kokonaisuus viimeinnen tunnettu tila vertailua varten
MNT={} #Mac --> Nimi
MIP={} #MAC --> IP
havaintoaika={} #MAC aikaleima Laitenähty viimeksi

def luoVisuaali():
    G = nx.Graph()
    for isan in meshnaapuridata: #käydään isäntien naapurit läpi
        for naap in meshnaapuridata[isan]["naapurit"]:
            naapuri=naap["laite"]
            if naapuri=='':
                break
            teho=naap["teho"]
            print(teho)
            G.add_edge(isan[-5:], naapuri[-5:], valimatka=int(40-float(teho)))
    pos = nx.spring_layout(G, seed=0)
    plt.figure(figsize=(9, 9))
    nx.draw(G, pos,with_labels = True, node_color ='blue', node_size=3000, font_size=8, font_color="yellow")
    edge_labels = nx.get_edge_attributes(G,'valimatka')
    nx.draw_networkx_edge_labels(G, pos, edge_labels = edge_labels)
    plt.savefig('static/kartta.png')
    #plt.clf()
    #plt.cla()
    plt.close()
    f.paivitaKuva()

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

class FlaskPalvelu:
    def __init__(self):
        #self.clientsMeshraspi=[]
        #self.clientsSelain=[]
        self.app = Flask(__name__)
        self.app.logger.disabled = True #hide flask messages
        log = logging.getLogger('werkzeug') #hide flask messages
        log.disabled = True #hide flask messages
        cli = sys.modules['flask.cli'] #hide flask messages
        cli.show_server_banner = lambda *x: None #hide flask messages
        self.app.config['SECRET_KEY'] = 'secret!'
        self.app.config['DEBUG'] = False
        self.socketio = SocketIO(self.app, async_mode='threading', logger=False, engineio_logger=False)
        fp=threading.Thread(target=self.palv)
        fp.start()

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.socketio.on('connect', namespace='/selain')
        def selain_connect():
            pass
            #self.clientsSelain.append(request.sid)

        @self.socketio.on('connect', namespace='/meshraspi')
        def meshraspi_connect():
            pass
            #self.clientsMeshraspi.append(request.sid)

        @self.socketio.on('disconnect', namespace='/meshraspi')
        def test_disconnect():
            pass
            #print('Client disconnected')

        @self.socketio.on('naapuri_message', namespace='/meshraspi') #client lähettää tietoa naapureistaan
        def __receiv_message(data):
            jdata=json.loads(data)
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

        @self.socketio.on('selainmsg', namespace='/selain') #selaimelta tulevia komentoja
        def __receiv_message(data):
            print("SSS",data)

    def lahetaMeshraspi(self,number):
        #for cl in self.clients:
            #self.socketio.emit('newnumber', {'number': cl}, room=cl, namespace='/meshraspi') #vain pyytäjälle
        self.socketio.emit('newnumber', {'number': number}, namespace='/meshraspi') #kaikille namespacessa

    def lahetaSelain(self,number):
        self.socketio.emit('naapuridata', {'data': number}, namespace='/selain') #kaikille namespacessa

    def paivitaKuva(self):
        #print("päivitä selaimen kuva")
        self.socketio.emit('paivitakuva', {'data': 0}, namespace='/selain') #kaikille namespacessa

    def palv(self):
        self.socketio.run(self.app, host='0.0.0.0', port=int(config.get("batnaapuri_portti")))

def tarkistaKadonneet(): # käydään läpi laitteiden viimeiset havaintoajat
    for laite in list(MNT):
        nahtyViimeksi=time.time()-havaintoaika[laite]
        if nahtyViimeksi >=10:
            #print("kadonnut", laite)
            del meshnaapuridata[laite]
            del MNT[laite]
            luoVisuaali()
        #print("MNT: ",laite, havaintoaika[laite])

if __name__ == '__main__':
    f=FlaskPalvelu()
    num=0
    while True:
        num+=1
        if num % 10 == 0:
            tarkistaKadonneet()
        #f.lahetaSelain("piip"+str(num))
        time.sleep(1)
