# raspberry-mesh
HUOM tikun ajuri   
git clone https://github.com/aircrack-ng/rtl8812au.git 

![](https://github.com/janttari/raspberry-mesh/raw/master/doc/mesh%20kaavio.png)

Asennus: 

    sudo raspi-config # --> Localisation Options --> Change WLAN Country
    sudo apt update && sudo apt install -y batctl git
    cd ~
    git clone https://github.com/janttari/raspberry-mesh.git


Suorita gateway:

    cd ~/raspberry-mesh
    ./meshgateway

Suorita client:

    cd ~/raspberry-mesh
    ./meshclient



TODO: 

 -ulkoisella tikulla ja MTU 1532
