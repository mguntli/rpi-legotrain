# rpi-legotrain
Raspberry Pi control of 12V lego train (with UniPi 1.1).
![UniPi 1.1](doc/UniPi-11-top.jpg?raw=true "UniPi")

# setup
Install EVOK (the UniPi API) for easy access to the UniPi 1.1 from Raspberry Pi.
```
sudo su
wget https://github.com/UniPiTechnology/evok/archive/2.4.10.zip
unzip 2.4.10.zip
cd evok-2.4.10
bash install-evok.sh
```

# wiring
/json/relay/1 --> Light Signal 1 red

/json/relay/2 --> Light Signal 1 green

/json/relay/3 --> Track 1

/json/relay/4 --> Track 2


/json/ai/1 --> not used

/json/ai/2 --> not used


/json/input/1 --> not used

/json/input/2 --> not used
