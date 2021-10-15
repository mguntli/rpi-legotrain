from enum import Enum
import requests
import time

class Rail(Enum):
    RAIL_1 = 1
    RAIL_2 = 2

class RelaisCircuit(str, Enum):
    LIGHT_SIGNAL_RAIL1 = "1"
    LIGHT_SIGNAL_RAIL2 = "2"
    TRACK_RAIL1 = "3"
    TRACK_RAIL2 = "4"
    RAIL_SWITCH1 = "5"

class RelaisValue(str, Enum):
    OFF = "0"
    ON = "1"

class State(Enum):
    INIT = 1
    PASSENGER_TRAIN_START = 2
    PASSENGER_TRAIN_RUN = 3
    PASSENGER_TRAIN_STOP = 4
    PAUSE_1 = 5
    GOODS_TRAIN_START = 6
    GOODS_TRAIN_RUN = 7
    GOODS_TRAIN_STOP = 8
    PAUSE_2 = 9

class SoundFiles(str, Enum):
    RAIL_1_LEAVES_STATION = "rail1LeavesStation.mp3"

server = "http://localhost:8080"
state = State.INIT

def init():
    stopTrain(Rail.RAIL_1)
    stopTrain(Rail.RAIL_2)
    state = State.INIT

def runTrain(rail):
    if (rail == Rail.RAIL_1):
        setRelay(RelaisCircuit.RAIL_SWITCH1, RelaisValue.ON);
        setRelay(RelaisCircuit.LIGHT_SIGNAL_RAIL1, RelaisValue.ON);
        setRelay(RelaisCircuit.TRACK_RAIL1, RelaisValue.ON);
    elif (rail == Rail.RAIL_2):
        setRelay(RelaisCircuit.RAIL_SWITCH, RelaisValue.OFF);
        setRelay(RelaisCircuit.LIGHT_SIGNAL_RAIL2, RelaisValue.ON);
        setRelay(RelaisCircuit.TRACK_RAIL2, RelaisValue.ON);

def stopTrain(rail):
    if (rail == Rail.RAIL_1):
        setRelay(RelaisCircuit.LIGHT_SIGNAL_RAIL1, RelaisValue.OFF);
        setRelay(RelaisCircuit.TRACK_RAIL1, RelaisValue.OFF);
    elif (rail == Rail.RAIL_2):
        setRelay(RelaisCircuit.LIGHT_SIGNAL_RAIL2, RelaisValue.OFF);
        setRelay(RelaisCircuit.TRACK_RAIL2, RelaisValue.OFF);

def isTrainAtStation(rail):
    return TRUE;

def setRelay(circuit, value):
    relaisUrl = server + "/json/relay/" + circuit
    relaisData = "{\"value\":\"" + value + "\"}"
    headers = {'content-type': 'application/json'}
    response = requests.request("POST", relaisUrl, data=relaisData, headers=headers)

def playSound(soundFile):
    print(soundFile)

def runStateMachine():
    global state
    if (state == State.INIT):
        if (isTrainAtStation(Rail.RAIL_1) && isTrainAtStation(Rail.RAIL_2)):
            state = State.PASSENGER_TRAIN_START
    elif (state == State.PASSENGER_TRAIN_START):
        playSound(SoundFiles.RAIL_1_LEAVES_STATION)
        runTrain(Rail.RAIL_1)
        state = State.PASSENGER_TRAIN_RUN

def main():
    init()
    while TRUE:
        runStateMachine

main()
