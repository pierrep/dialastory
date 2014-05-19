#!/usr/bin/env python
import time
import pyaudio
import pygame
import wave
import os
import tempfile
from puffin_record import *
from keyboard import Keyboard
import select
import termios
import logging
import serial
import sys

class PuffinSm(object):
    #XXX Fix this to match the target platform 
    #configuration data
    logfile = "./puffin.log"
    mp3_root = "/home/penguinphone/dialastory/mp3s/"
    intro_mp3="audio/Saffran Intro.mp3"
    mistake_mp3="audio/Saffran Mistake.mp3"
    switchboard_mp3 = "audio/All Numbers.mp3"
    welcome_mp3 = "audio/Saffran Intro.mp3"
    dispenserDevices = [
	"/dev/ttyUSB0",
#        "/dev/serial/by-path/platform-bcm2708_usb-usb-0:1.3.1:1.0-port0",
        "/dev/serial/by-path/platform-bcm2708_usb-usb-0:1.3.5:1.0-port0",
        "/dev/serial/by-path/platform-bcm2708_usb-usb-0:1.3.2:1.0-port0",
        "/dev/serial/by-path/platform-bcm2708_usb-usb-0:1.3.3:1.0-port0",
        "/dev/serial/by-path/platform-bcm2708_usb-usb-0:1.3.5:1.0-port0"
        ]

    scannerKeyDev = [
	"/dev/input/event0",
#        "/dev/input/by-path/platform-bcm2708_usb-usb-0:1.2.5:1.0-event-kbd",
        "/dev/input/by-path/platform-bcm2708_usb-usb-0:1.3.7.3:1.0-event-kbd",
        "/dev/input/by-path/platform-bcm2708_usb-usb-0:1.3.7.1.2:1.0-event-kbd",
        "/dev/input/by-path/platform-bcm2708_usb-usb-0:1.3.7.1.3:1.0-event-kbd",
        "/dev/input/by-path/platform-bcm2708_usb-usb-0:1.3.7.3:1.0-event-kbd"
    ]
    arduinoFile = "/dev/ttyACM0"


    #State enumerations and current state variables
    STATE_IDLE = 0
    STATE_SWITCHBOARD = 1
    STATE_WELCOME =2
    STATE_PLAYING_AUTHOR=3
    STATE_RECORDING_RESPONSE=4
    STATE_DISPENSE_AND_PAIR=8
    STATE_RING = 10
    state = 0
    last_lift_time = None


    def reset_arduino(self):
        #self.ser.flushInput()
        self.ser.write('8')
        #time.sleep(0.01)


    ##### XXX These methods MUST be  filled in to match the hardware

    def read_arduino(self, sleep=True):
        try:
            line = self.ser.readline()
            #self.write_log("Arduino = " + str(line))
            #if (sleep):
               #time.sleep(0.05)
            key = line.split(':')[1].lstrip().rstrip()
            if (len(key) == 0):
                key = None
            hang = line.split(':')[0].lstrip().rstrip()
            return (line.split(':')[0].lstrip().rstrip() == '0', key);
        except:
            return (False,None)


    def dispense_and_scan(self, author_selection):
        j = 0
        #f = open(self.dispenserDevices[0], "wb")
        f = open("/dev/ttyUSB0", "wb")
        f.write("020180000380".decode("hex"))
        f.flush()
        f.close()
        #k = Keyboard(self.scannerKeyDev[0])
        k = Keyboard("/dev/input/event0")
        k.flush()
        code = ""
        i = 0
        #return code
        start_time = time.time()
        while i < 8:
            key = k.readKey()
            #print key
            if key is not None:
                code += key
                i += 1
            end_time = time.time() - start_time 
            #self.write_log("end time = "+str(end_time))
            if(end_time > 4):
                self.write_log("reader time out!!")
                break;
        self.write_log("Dispensing from card dispenser " + str(0))
        self.write_log("device = "+str(self.dispenserDevices[0]))
        self.write_log("scanner device = "+str(self.scannerKeyDev[0]))
        return code

    def sound_ringer(self):
        f = open(self.arduinoFile, "wb")
        f.write('6')
        f.flush()
        f.close()

    def sound_ended(self):
        for event in pygame.event.get():
            if (event.type == self.TRACK_END):
                self.write_log("sound ended!")
                return True
        return False

    def lightOn(self):
        f=open(self.arduinoFile, "wb")
        f.write('1')
        f.flush()
        f.close()

    def lightOff(self):
        f=open(self.arduinoFile, "wb")
        f.write('0')
        f.flush()
        f.close()


    def write_log(self, string):
        #self.log.write(time.ctime() + '|' + string)
	    logging.info(string)

    def __init__(self):
        self.state = self.STATE_IDLE
        self.last_lift_time = time.time()
        pygame.init() #event subsystem is in the core
        pygame.mixer.init()
        self.TRACK_END = pygame.USEREVENT+1
        pygame.mixer.music.set_endevent(self.TRACK_END)
        pygame.event.clear(self.TRACK_END)
        self.author_selection = 0
        logging.basicConfig(filename=self.logfile, datefmt='%m/%d/%Y %I:%M%p', format='%(levelname)s:%(asctime)s: %(message)s',level=logging.INFO)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logging.getLogger('').addHandler(console)
	#enable logging here:
	#logging.getLogger('').disabled = True
        self.write_log("Initialised state machine\n")
        #self.lightOn()
        self.ser = serial.Serial(self.arduinoFile,115200,timeout=2)
    
        #barcode = self.dispense_and_scan(3)
        #self.write_log("barcode = " +str(barcode))

    def runState(self):
        #detect hangup and return to idle:
        if not self.read_arduino()[0] and self.state != self.STATE_IDLE and self.state != self.STATE_DISPENSE_AND_PAIR:
            self.state = self.STATE_IDLE
            self.write_log("Handset replaced, terminating session\n")
            pygame.mixer.music.stop()
            pygame.event.clear(self.TRACK_END)
            self.write_log("Entering Idle State...")

        if  self.state == self.STATE_IDLE:
            #self.write_log("Idle State...")
            self.authorselection = 0
            self.tmpfile = None
            if (time.time() - self.last_lift_time) > 300:
            	#self.sound_ringer()
            	self.write_log("Reached 300 second timeout, sounding ringer\n")
            	self.last_lift_time = time.time()

            if (self.read_arduino()[0]):
                self.last_lift_time = time.time()
                self.state = self.STATE_WELCOME
                self.write_log("Playing welcome")

        elif self.state == self.STATE_SWITCHBOARD:
            pygame.event.clear(self.TRACK_END);
            pygame.mixer.music.load(self.switchboard_mp3)
            pygame.mixer.music.play()
            self.write_log("Playing switchboard options")
            #wait until the sound clip ends then repeat
            while (not self.sound_ended()):
                (lifted,key) = self.read_arduino()
                if (not lifted):
                    self.write_log("User hung up!")
                    break
                if (key is not None and (key == "1" or key == "2" or key == "3" or key == "4" or key == "5")):
                    self.write_log("User pressed key "+key) 
                    self.write_log("User selected author %s\n" % key)
                    self.author_selection = int(key)-1
                    self.state = self.STATE_PLAYING_AUTHOR
                    pygame.mixer.music.stop()
                    break
                elif key is not None:
                    self.reset_arduino()
                    self.write_log("User pressed wrong key "+key) 
                    pygame.mixer.music.load(self.mistake_mp3)
                    pygame.mixer.music.play()
                    while (not self.sound_ended()):
                        pass
                    #play it again!
                    break;

        elif self.state == self.STATE_WELCOME:
            pygame.mixer.music.load(self.welcome_mp3)
            pygame.mixer.music.play()
            #self.write_log("Playing welcome\n")
            #user must wait for completion of the welcome before we continue

            if (self.read_arduino()[0]):
                self.write_log("receiver picked up...")
            else:
                self.write_log("receiver put down!")
            while (not self.sound_ended() and self.read_arduino()[0]):
                pass
            self.reset_arduino()
            self.state = self.STATE_SWITCHBOARD

        elif self.state == self.STATE_PLAYING_AUTHOR:
            #pygame.mixer.music.load(self.author_mp3[self.author_selection])
	    #author_mp3 = "audio/Author" + str(self.author_selection + 1) + "short" + ".mp3"
	    author_mp3 = "audio/Author" + str(self.author_selection + 1) + ".mp3"
            pygame.mixer.music.load(author_mp3)
            pygame.mixer.music.play()
            self.write_log("Playing " + author_mp3 )
            #user must wait for completion of the welcome before we continue
            while (not self.sound_ended() and self.read_arduino()[0]):
                pass

            self.state = self.STATE_RECORDING_RESPONSE

        elif self.state == self.STATE_RECORDING_RESPONSE:
            self.write_log("User recording response\n")
            start_time = time.time()
            self.tmpwav = tempfile.mkstemp()[1]
            recorder = WavRecord(self.tmpwav)
            recorder.start()
            while (time.time() - start_time < 240 and self.read_arduino(sleep=False)[0]):
                pass
            recorder.stop()
            if (time.time() - start_time) < 3:
                self.write_log("Short recording of < 3 seconds detected, discarding")
                os.unlink(self.tmpwav)
                self.state = self.STATE_IDLE
            else:
                self.write_log("User response recorded, %d seconds long" % (time.time()-start_time))
                self.state = self.STATE_DISPENSE_AND_PAIR

        elif self.state == self.STATE_DISPENSE_AND_PAIR:
            barcode = self.dispense_and_scan(self.author_selection)
            self.write_log("Dispensing card and pairing audio from dispenser %d, barcode %s\n" % (self.author_selection, barcode))
            if barcode is "":
                #unable to pair, just compress and store with the current ctime
                comp = Mp3Store(self.tmpwav, str(int(time.time()))+ ".mp3", self.mp3_root)
                comp.compress()
            else:
                comp = Mp3Store(self.tmpwav, barcode + ".mp3", self.mp3_root)
                comp.compress()
            os.unlink(self.tmpwav)
            self.state = self.STATE_IDLE
            self.last_lift_time = time.time()
            sys.exit(0)

        else:
            self.state = self.STATE_IDLE
            self.last_lift_time = time.time()

