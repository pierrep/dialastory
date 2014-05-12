#!/usr/bin/env python
import struct
import time
import sys
import select
import os

class Keyboard(object):
    fname = None
    ifile = None
    event_format = "IIHHI"
    key_1 = 2
    key_2 = 3
    key_3 = 4
    key_4 = 5
    key_5 = 6
    key_6 = 7
    key_7 = 8
    key_8 = 9
    key_9 = 10
    key_0 = 11


    def __init__(self, fname):
        self.fname = fname
        self.ifile = os.open(self.fname, os.O_RDONLY|os.O_NONBLOCK)

    def flush(self):
        pass

    def readKey(self):
        try:
            event = os.read(self.ifile, 16)
            while (event):
                (tv_sec, tv_usec, type, code, value) = struct.unpack(self.event_format, event)
                if type == 1 and code != 0 and value == 0:
                    return self.decodeKey(code)
                event = os.read(self.ifile, 16)
        except:
            return None

    def decodeKey(self, key):
        if (key == self.key_1):
            return '1'
        if (key == self.key_2):
            return '2'
        if (key == self.key_3):
            return '3'
        if (key == self.key_4):
            return '4'
        if (key == self.key_5):
            return '5'
        if (key == self.key_6):
            return '6'
        if (key == self.key_7):
            return '7'
        if (key == self.key_8):
            return '8'
        if (key == self.key_9):
            return '9'
        if (key == self.key_0):
            return '0'

if (__name__ == "__main__"):
    k=Keyboard("/dev/input/event1")
    while True:
        key = k.readKey()
        if key is not None:
            print key
