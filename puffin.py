#!/usr/bin/python
import puffin_sm
import os
import time
import signal
import sys

def signal_handler(signal,frame):
    print '\nCtrl-C pressed....exiting!'
    sys.exit(0)

if __name__ == "__main__":
    os.system("stty -F /dev/ttyACM0 115200")
    os.system("stty -F /dev/ttyUSB0 19200")
    os.system("stty -F /dev/ttyUSB1 19200")
    os.system("stty -F /dev/ttyUSB2 19200")
    os.system("stty -F /dev/ttyUSB3 19200")
    os.system("stty -F /dev/ttyUSB4 19200")

    signal.signal(signal.SIGINT, signal_handler)    

    sm = puffin_sm.PuffinSm()
    while (True):
        sm.runState()
