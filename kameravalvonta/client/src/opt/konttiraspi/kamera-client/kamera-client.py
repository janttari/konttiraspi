#!/usr/bin/env python3

# Luo liiketunnistuksen tapahduttua HLS-videoita sekunnin slaisseina.
# kirjoitetaan ffmpegille videoio:n avulla frame kerrallaan.
# kun ffmpeg on saanut sekunnin verran frameja, se kirjoittaa
# ts-siivun ja päivittää m3u8 tiedoston.
# Palvelimelle lähetetään pelkkä .ts ja palvelin luo itse m3u8-tiedoston
#
# prebuffer = montako sekuntia ennen liiketapahtumaa tallennetaan
# postbuffer = montako sekuntia liiketapahtuman jälkeen tallennetaan
# vidTempDir = hakemisto jonne videot luodaan 
# video_capture = cv2.VideoCapture(0) = /dev/video0
#
#
#   sudo apt update
#   sudo apt install -y libatlas-base-dev python3-pip
#   sudo pip3 install imutils opencv-python 
#   
# TODO: -laatuasetukset
#       
#

import warnings
import datetime
import imutils
import json
import time
import cv2
import sys
import numpy as np
from videoio import VideoWriter
import os
import glob
import subprocess
import threading
import asyncio
import aiohttp
from configobj import ConfigObj

config=ConfigObj('/boot/asetukset.txt')
############################### ASETUKSET ########################################
camNimi="Cam1" #KIRJOITA TÄMÄ KUVAAN KAMERAN NIMEKSI
uploadurl = config.get('cam_serverurl') #POSTaa tänne videot
vidTempDir= config.get('cam_clienttmpdir') #TALLENNA VIDEOT TÄNNE TILAPÄISESTI
prepuffer=5 #VIDEOON SISÄLLYTETÄÄN N SEKUNTIA ENNEN LIIKETAPAHTUMAA
postbuffer=5 #VIDEOON SISÄLLYTETÄÄN N SEKUNTIA LIIKETAPAHTUMAN JÄLKEEN
MINAREA=70000 #VAADITTAVA MUUTOS KUVASSA JOKA AIHEUTTAA LIIKETUNNISTUKSEN
RESX=1280
RESY=720
DELTA_TRESH=1
SHOWVIDEO=True #NÄYTETÄÄNKÖ KUVA IKKUNASSA
MINMOTIONFRAMES=5 #LIIKETTÄ ESIINNYTTÄVÄ VÄHINTÄÄN N FRAMESSA JOTTA TULKITAAN LIIKKEEKSI
##################################################################################



async def lahetaPalvelimelle(tiedosto, soittolista, extinf): #POST ts-tiedosto palvelimelle
    global uploadurl
    with open(tiedosto, 'rb') as f:
        async with aiohttp.ClientSession() as session:
            async with session.post(uploadurl, data={'video': f, 'soittolista': soittolista, 'extinf': extinf}) as response:
                #os.remove(tiedosto)
                return await response.text()

def valvoM3u8(m3u8): # valvoo  m3u8-tiedostojen ilmesymisiä ja kasvamisia
    lahetetyt=[] #jo lähetetyt ts-tiedostot tähän {soittolista: [tiedosto1, tiedosto2,tied...]}
    bsoittolista=os.path.split(m3u8)[1] #soittolista ilman polkua
    valmis=False
    extinf="#EXTINF:1.00"
    while not valmis:
        if os.path.isfile(m3u8): #ffmpeg ei välttämättä ole vielä ehtinyt kirjoittaa
            with open(m3u8, "r") as m3u8filu:
                rivit = m3u8filu.readlines()
            for rivi in rivit:
                rivi=rivi.rstrip()
                if rivi.startswith('#EXTINF:'): #extinf-rivi
                    extinf=rivi
                elif not rivi.startswith("#"): #jos rivi ei ala #, siinä kerrotaan ts-tiedoston nimi
                    videofilu=vidTempDir+"/"+rivi
                    if not videofilu in lahetetyt: #jos tiedostoa ei ole vielä upattu palvelimelle
                        #print("LAH", videofilu,bsoittolista,extinf)
                        loop.create_task(lahetaPalvelimelle(videofilu, bsoittolista, extinf))
                        lahetetyt.append(videofilu)
                        #palanumero+=1
            if rivi == "#EXT-X-ENDLIST": #ffmpeg on kirjoittanut HLS:n valmiiksi
                valmis=True
                #os.remove(m3u8)
        time.sleep(0.5)

#OPENCV MAIN-LOOPPI
async def ocv_main():
    vidm3u8Nimi="video" #tähän kirjoitettavan videon nimi. aseteteean myöhemmin
    framemuisti=[]
    liike_kaynnissa=False
    liike_pois_laskuri=0 #kasvatetaan joka kierroksella kun ei liikettä
    liike_alkaa_laskuri=0 #kasvatetaan aina kun liikettä havaitaan
    ruutu=0
    warnings.filterwarnings("ignore")
    os.makedirs(vidTempDir, exist_ok=True)
    video_capture = cv2.VideoCapture(config.get('cam_device')) #pylint: disable=no-member
    if (video_capture.isOpened() == False):
        print('!!! Kameraa ei saatu avattua')
        sys.exit(-1)

    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, RESX) #pylint: disable=no-member
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, RESY) #pylint: disable=no-member
    print("[INFO] warming up...")
    time.sleep(3)
    avg = None
    fps = int(video_capture.get(cv2.CAP_PROP_FPS)) #pylint: disable=no-member
    print("FPS",fps)
    wait_ms = int(1000/fps)
    print(wait_ms)

    while True:
        fps = int(video_capture.get(cv2.CAP_PROP_FPS)) #pylint: disable=no-member
        ret, frame = video_capture.read()
        timestamp = datetime.datetime.now()
        if liike_kaynnissa:
            liike_pois_laskuri+=1
            if liike_pois_laskuri>postbuffer*fps: #**LIIKE PÄÄTTYI**
                liike_alkaa_laskuri=0
                ffTallenna.close() #pylint: disable=used-before-assignment
                liike_kaynnissa=False
                text = "Unoccupied"

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #pylint: disable=no-member
        gray = cv2.GaussianBlur(gray, (21, 21), 0) #pylint: disable=no-member

        if avg is None:
            #print("[INFO] starting background model...")
            avg = gray.copy().astype("float")
            continue

        cv2.accumulateWeighted(gray, avg, 0.5) # pylint: disable=no-member
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg)) #pylint: disable=no-member

        thresh = cv2.threshold(frameDelta, DELTA_TRESH, 255, cv2.THRESH_BINARY)[1] #pylint: disable=no-member
        thresh = cv2.dilate(thresh, None, iterations=2) #pylint: disable=no-member
        cnts,image= cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #pylint: disable=no-member

        for c in cnts:
            if cv2.contourArea(c) < MINAREA: #pylint: disable=no-member
                continue
            (x, y, w, h) = cv2.boundingRect(c) #pylint: disable=no-member
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2) #pylint: disable=no-member
            liike_pois_laskuri=0
            if not liike_kaynnissa: 
                liike_alkaa_laskuri+=1
                if liike_alkaa_laskuri>=MINMOTIONFRAMES: # **LIIKE ALKOI**
                    text = "Occupied" 
                    vidm3u8Nimi= vidTempDir+"/"+datetime.datetime.now().strftime("%y%m%d-%H%M%S")+"-"+camNimi+".m3u8"  #annetaan tässä videolle nimi aikaleiman mukaan
                    #HUOMAA ETTÄ video_rgb:ssä on nyt jokainen frame keyframe!
                    ffTallenna=VideoWriter(vidm3u8Nimi,(RESX,RESY),preset="medium",fps=fps, lossless=False)
                    liike_kaynnissa=True
                    loop.run_in_executor(None, valvoM3u8, vidm3u8Nimi)
                          
        ts = " "+camNimi+" "+ timestamp.strftime("%y%m%d-%H%M%S")+"  "+str(ruutu)
        cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1) #pylint: disable=no-member
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #pylint: disable=no-member
        framemuisti.append(rgb) #lisätään frame muistiin
        ruutu+=1


        if not liike_kaynnissa:
            if len(framemuisti)>fps*prepuffer:
                framemuisti.pop(0) #poistetaan eka frame
        else: #liike on käynnissä
            fpit=len(framemuisti)
            for ff in range(0,fpit):
                ffTallenna.write(framemuisti[ff])
            framemuisti=[]
            #del framemuisti[:fpit]

        if SHOWVIDEO:
            cv2.imshow("Security Feed", frame) #pylint: disable=no-member
            if cv2.waitKey(1) & 0xFF == ord('q'): #pylint: disable=no-member
                break
        await asyncio.sleep(1/(wait_ms-1))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ocv_main())


