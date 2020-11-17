# konttiraspi  
## Asennus:  
Asenna Raspbian OS Lite muistitikulle ja sen jälkeen siirrä tiedostot  
**asenna_konttiraspi** ja **asetukset.txt** muistikortin /-boot osiolle.  
(Tässä vaiheessa kortin voi kloonata halutessaan helpottaa muiden Raspien asennusta)  
  
Kirjaudu Raspille ja:  

    cd /boot  
    ./asenna_konttiraspi  
  
Valitse asennettavat palvelut:  
![](https://raw.githubusercontent.com/janttari/konttiraspi/main/doc/konttiraspivalikko.png)  


## Päivittäminen:  
Lataa uusi **asenna_konttiraspi** muistikortin /boot osiolle.  
Lataaminen päätteessä:
  
    cd /boot  
    rm asenna_konttiraspi #Poista vanha tiedosto jos sellainen on.  
    wget https://raw.githubusercontent.com/janttari/konttiraspi/main/asenna_konttiraspi  
  

Jos haluat muuttaa asennuksen ominaisuuksia (valikot):  

    cd /boot    
    ./asenna_konttiraspi
  
Jos haluat vain päivittää olemassa olevat ominaisuudet (ilman valikoita):
  
    cd /boot  
    ./asenna_konttiraspi -u
  
Asennuksen ja päivityksen jälkeen uudelleenkäynnistys pitää tehdä:  
  
    sudo reboot
  
## Asetukset:
Kaikki asetukset on tiedostossa **/boot/asetukset.txt**  
Tarkista ne huolellisesti.  
  

-------
HUOM! Yhteyksien luominen käynnistyksen jälkeen ja yhteyden katkettua voi kestää useamman minuutin!  
  

-------

**konttiraspi-system** sisältää perustoiminnot. Asennetaan kaikkiin Raspeihin.  
**konttiraspi-mesh-client** sisältää mesh-client ja batnaapurit-client.  
**konttiraspi-mesh-gateway**  sisältää mesh-gateway ja batnaapurit-server.  
**konttiraspi-sahkomittari-client**  sähkömittareja lukeville Raspeille. Lukee sarjaportista Arduinon datan ja lähettää sen sahkomittari-serverille  
**konttiraspi-sahkomittari-server**  


