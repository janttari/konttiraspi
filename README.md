# konttiraspi  
## Asennus:  
Asenna Raspbian OS Lite muistitikulle ja tee tiedosto ssh boot-osiolle.


Kirjaudu Raspille ja:  

    sudo apt update
    cd ~
    wget https://raw.githubusercontent.com/janttari/konttiraspi/main/asenna_konttiraspi  
    chmod a+x asenna_konttiraspi  
    ./asenna_konttiraspi  
  
Valitse asennettavat palvelut:  
![](https://raw.githubusercontent.com/janttari/konttiraspi/main/doc/konttiraspivalikko.png)  

Säädä asetukset:
  
    sudo nano /boot/asetukset.txt
    



## Päivittäminen:  
 
Lataaminen päätteessä:
  
    cd ~ 
    rm asenna_konttiraspi #Poista vanha tiedosto jos sellainen on.  
    wget https://raw.githubusercontent.com/janttari/konttiraspi/main/asenna_konttiraspi  
    chmod a+x asenna_konttiraspi  
  

Jos haluat muuttaa asennuksen ominaisuuksia (valikot):  
 
    ./asenna_konttiraspi
  
Jos haluat vain päivittää olemassa olevat ominaisuudet (ilman valikoita pelkkä päivitys):
  
    ./asenna_konttiraspi -u
  
Asennuksen ja päivityksen jälkeen uudelleenkäynnistys pitää tehdä:  
  
    sudo reboot
  
## Asetukset:
Kaikki asetukset on tiedostossa **[/boot/asetukset.txt](deb/asetukset.txt)**    
Tarkista ne huolellisesti.  
  

-------
HUOM! Yhteyksien luominen käynnistyksen jälkeen ja yhteyden katkettua voi kestää useamman minuutin!  
  

-------

**konttiraspi-system** sisältää perustoiminnot. Asennetaan kaikkiin Raspeihin.  
  
**konttiraspi-mesh-client** sisältää mesh-client ja batnaapurit-client.  
* mesh-client toimii mesh-verkon asiakkaana ja ottaa yhteyden gateway-raspiin (ja sitä kautta internetiin)    
* batnaapurit-client ilmoittaa näkemistään mesh-verkon laitteista serverille
  
**konttiraspi-mesh-gateway**  sisältää mesh-gateway ja batnaapurit-server  
* mesh-gateway toimii mesh-verkon gatewayna  
* batnaapurit-server pitää kirjaa mesh-verkon laitteista ja ws palvelee selainta portissa 8090    
  
  
**konttiraspi-sahkomittari-client**  
* sähkömittareja lukeville Raspeille. Lukee sarjaportista Arduinon datan ja lähettää sen sahkomittari-serverille  
  
**konttiraspi-sahkomittari-server**  
* ws palvelee selainta portissa 8889  


-------
TODO:

** websocketit asynciolle  

  

