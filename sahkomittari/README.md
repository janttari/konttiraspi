# sahkomittari
asennus **RASPBERRY CLIENT**:  
```diff
+ Tämä versio ottaa vastaan sarjaportin kautta Arduinon lähettämän datan  
```

Asetukset tiedostoissa:
```
/boot/asetukset.txt #esim sarjaportti, pulssia/kwh jne LAITA TÄNNE PALVELIMEN OSOITE!
```

SERVERI:  
asentuu /opt/konttiraspi/sahkomittari/server
mene internet-selaimella http://raspi_server_ip  
  
  
tietokanta asiakkaille:  
/opt/kottiraspi/sahkomittari/server/data/asiakkaat.db #muokataan selaimella  
  
tietokanta kulutuslukemille:  
/opt/konttiraspi/sahkomittari/server/data/kulutus.db #tänne tallennetaan pysyvät lukemat tasatunnein  
  
  
TODO:  
  
+PÄIVITÄ POLUT, NE ON NYT MUUTOKSEN JÄLKEEN VÄÄRIN!
