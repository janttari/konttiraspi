# konttiraspi  
Asennus:  
Asenna Raspbian OS Lite muistitikulle ja sen jälkeen siirrä tiedostot  
**asenna_konttiraspi** ja **asetukset.txt** muistikortin /-boot osiolle.  
(Tässä vaiheessa kortin voi kloonata halutessaan helpottaa muiden Raspien asennusta)  
  
Kirjaudu Raspille ja:  

    cd /boot  
    ./asenna_konttiraspi  
  
  
Päivittäminen:  
Lataa uusi asenna_konttiraspi muistikortin /boot osiolle.  
  
Jos haluat muuttaa asennuksen ominaisuuksia (valikot):  
  
    ./asenna_konttiraspi
  
Jos haluat vain päivittää olemassa olevat ominaisuudet (ilman valikoita):
  
    ./asenna_konttiraspi -u
  
Asennuksen ja päivityksen jälkeen uudelleenkäynnistys pitää tehdä:  
  
    sudo reboot
  
