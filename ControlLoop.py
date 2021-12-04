from enum import Enum
from dataclasses import dataclass
import requests
import time
import pygame
import vlc

class RelaisCircuit(str, Enum):
    LIGHT_SIGNAL_1_GREEN = "1"
    LIGHT_SIGNAL_1_RED = "2"
    TRACK_RAIL1 = "7"
    TRACK_RAIL2 = "8"

class RelaisValue(str, Enum):
    OFF = "0"
    ON = "1"

class SignalValue(str, Enum):
    GREEN = "0"
    RED = "1"

class SignalId(str, Enum):
    SIGNAL_1 = "Signal 1"
    SIGNAL_2 = "Signal 2"

class Rail(str, Enum):
    RAIL_1 = "Rail 1"
    RAIL_2 = "Rail 2"

class State(str, Enum):
    INIT = "Init"
    TRAIN_START = "Train start"
    TRAIN_RUN = "Train run"
    TRAIN_STOP = "Train stop"
    PAUSE = "Pause"

class SoundFiles(str, Enum):
    WHISTLE = "/home/pi/Desktop/rpi-legotrain/Whistle.mp3"

@dataclass
class StateMachineData:
    rail: Rail
    state: State
    startTime: float
    runtimeSeconds: int
    pauseSeconds: int

server = "http://localhost:8080"
RUNTIME_PASSENGER_TRAIN_SECONDS = 40
RUNTIME_GOODS_TRAIN_SECONDS = 20
PAUSE_PASSENGER_TRAIN_SECONDS = 25
PAUSE_GOODS_TRAIN_SECONDS = 20

def init():
    stopTrain(Rail.RAIL_1)
    stopTrain(Rail.RAIL_2)
    state = State.INIT
    initSound()

def setSignal(signal, signalValue):
    if (signal == SignalId.SIGNAL_1):
        if (signalValue == SignalValue.GREEN):
            setRelay(RelaisCircuit.LIGHT_SIGNAL_1_RED, RelaisValue.OFF)
            setRelay(RelaisCircuit.LIGHT_SIGNAL_1_GREEN, RelaisValue.ON)
        elif (signalValue == SignalValue.RED):
            setRelay(RelaisCircuit.LIGHT_SIGNAL_1_GREEN, RelaisValue.OFF)
            setRelay(RelaisCircuit.LIGHT_SIGNAL_1_RED, RelaisValue.ON)

def runTrain(rail):
    if (rail == Rail.RAIL_1):
        setSignal(SignalId.SIGNAL_1, SignalValue.GREEN)
        setRelay(RelaisCircuit.TRACK_RAIL1, RelaisValue.ON)
    elif (rail == Rail.RAIL_2):
        setRelay(RelaisCircuit.TRACK_RAIL2, RelaisValue.ON)

def stopTrain(rail):
    if (rail == Rail.RAIL_1):
        setSignal(SignalId.SIGNAL_1, SignalValue.RED)
        setRelay(RelaisCircuit.TRACK_RAIL1, RelaisValue.OFF)
    elif (rail == Rail.RAIL_2):
        setRelay(RelaisCircuit.TRACK_RAIL2, RelaisValue.OFF)

def setRelay(circuit, value):
    relaisUrl = server + "/json/relay/" + circuit
    relaisData = "{\"value\":\"" + value + "\"}"
    headers = {'content-type': 'application/json'}
    response = requests.request("POST", relaisUrl, data=relaisData, headers=headers)

def initSound():
    pygame.mixer.init()

def playBackgroundMusic():      
    instance = vlc.Instance()
    media_list = instance.media_list_new(['/home/pi/Desktop/rpi-legotrain/music/John Williams - Home Alone Soundtrack.mp3'])
    list_player = instance.media_list_player_new()
    list_player.set_media_list(media_list)
    list_player.set_playback_mode(vlc.PlaybackMode.loop)
    list_player.play()

def playSound(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()

def runStateMachine(data):
    oldState = data.state;
    
    if data.state == State.INIT:
        data.state = State.TRAIN_START
    elif data.state == State.TRAIN_START:
        playSound(SoundFiles.WHISTLE)
        time.sleep(2.0)
        runTrain(data.rail)
        data.startTime = time.monotonic()
        data.state = State.TRAIN_RUN
    elif data.state == State.TRAIN_RUN:
        if (time.monotonic() - data.startTime >= data.runtimeSeconds):
            stopTrain(data.rail)
            data.state = State.TRAIN_STOP
    elif data.state == State.TRAIN_STOP:
        data.startTime = time.monotonic()
        data.state = State.PAUSE
    elif data.state == State.PAUSE:
        if (time.monotonic() - data.startTime >= data.pauseSeconds):
            data.state = State.TRAIN_START
    
    if (oldState != data.state):
        print(data.state.value + ": " + data.rail.value)

def main():
    init()
    playBackgroundMusic()
    
    passengerTrain = StateMachineData(Rail.RAIL_1, State.INIT, 0, RUNTIME_PASSENGER_TRAIN_SECONDS, PAUSE_PASSENGER_TRAIN_SECONDS)
    goodsTrain = StateMachineData(Rail.RAIL_2, State.INIT, 0, RUNTIME_GOODS_TRAIN_SECONDS, PAUSE_GOODS_TRAIN_SECONDS)
    while True:
        runStateMachine(passengerTrain)
        runStateMachine(goodsTrain)
main()
