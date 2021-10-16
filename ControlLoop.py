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

class State(str, Enum):
    INIT = "Init"
    PASSENGER_TRAIN_START = "Passenger train start"
    PASSENGER_TRAIN_RUN = "Passenger train run"
    PASSENGER_TRAIN_STOP = "Passenger train stop"
    PAUSE_1 = "Pause 1"
    GOODS_TRAIN_START = "Goods train start"
    GOODS_TRAIN_RUN = "Goods train run"
    GOODS_TRAIN_STOP = "Goods train stop"
    PAUSE_2 = "Pause 2"

class SoundFiles(str, Enum):
    RAIL_1_LEAVES_STATION = "rail1LeavesStation.mp3"
    RAIL_1_ARRIVES_STATION = "rail1ArrivesStation.mp3"

server = "http://localhost:8080"
state = State.INIT
startTime = time.monotonic()
RUNTIME_PASSENGER_TRAIN_SECONDS = 10
RUNTIME_GOODS_TRAIN_SECONDS = 10
PAUSE_1_SECONDS = 10
PAUSE_2_SECONDS = 10

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
        setRelay(RelaisCircuit.RAIL_SWITCH1, RelaisValue.OFF);
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
    return True;

def setRelay(circuit, value):
    relaisUrl = server + "/json/relay/" + circuit
    relaisData = "{\"value\":\"" + value + "\"}"
    headers = {'content-type': 'application/json'}
    response = requests.request("POST", relaisUrl, data=relaisData, headers=headers)

def playSound(soundFile):
    print(soundFile)

def runStateMachine():
    global state
    global startTime
    oldState = state;
    
    if state == State.INIT:
        if isTrainAtStation(Rail.RAIL_1) and isTrainAtStation(Rail.RAIL_2):
            state = State.PASSENGER_TRAIN_START
    elif state == State.PASSENGER_TRAIN_START:
        playSound(SoundFiles.RAIL_1_LEAVES_STATION)
        runTrain(Rail.RAIL_1)
        startTime = time.monotonic()
        state = State.PASSENGER_TRAIN_RUN
    elif state == State.PASSENGER_TRAIN_RUN:
        if (time.monotonic() - startTime >= RUNTIME_PASSENGER_TRAIN_SECONDS):
            stopTrain(Rail.RAIL_1)
            playSound(SoundFiles.RAIL_1_ARRIVES_STATION)
            state = State.PASSENGER_TRAIN_STOP
    elif state == State.PASSENGER_TRAIN_STOP:
        if isTrainAtStation(Rail.RAIL_1):
            startTime = time.monotonic()
            state = State.PAUSE_1
    elif state == State.PAUSE_1:
        if (time.monotonic() - startTime >= PAUSE_1_SECONDS):
            state = State.GOODS_TRAIN_START
    elif state == State.GOODS_TRAIN_START:
        runTrain(Rail.RAIL_2)
        startTime = time.monotonic()
        state = State.GOODS_TRAIN_RUN
    elif state == State.GOODS_TRAIN_RUN:
        if (time.monotonic() - startTime >= RUNTIME_GOODS_TRAIN_SECONDS):
            stopTrain(Rail.RAIL_2)
            state = State.GOODS_TRAIN_STOP
    elif state == State.GOODS_TRAIN_STOP:
        if isTrainAtStation(Rail.RAIL_2):
            startTime = time.monotonic()
            state = State.PAUSE_2
    elif state == State.PAUSE_2:
        if (time.monotonic() - startTime >= PAUSE_2_SECONDS):
            state = State.PASSENGER_TRAIN_START
    
    if (oldState != state):
        print(state.value)

def main():
    init()
    while True:
        runStateMachine()
main()
