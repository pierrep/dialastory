#!/usr/bin/env python
import pyaudio
import wave
import os
import pygame

class WavRecord(object):
    fname = None
    stream = None
    wave = None
    sampleRate = 32000
    chunkSize = 4096
    doRecord = None
    def __init__(self, fname):
        self.fname = fname
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paInt16, channels=1,
                    rate=self.sampleRate, input=True, output=False,
                    frames_per_buffer=self.chunkSize, stream_callback=self.callback)
        self.wave = wave.open(self.fname, "wb")
        self.wave.setnchannels(1)
        self.wave.setframerate(self.sampleRate)
        self.wave.setsampwidth(2)

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.wave.close()

    def callback(self, in_data, frame_count, time_info, status_flags):
        if (self.doRecord is not None):
            self.wave.writeframes(in_data)
        return ("",0)

    def start(self):
        self.doRecord = 1

    def stop(self):
        self.doRecord = None

class Mp3Store(object):
    def __init__(self, wavname, mp3name):
        self.wavname = wavname
        self.mp3name = mp3name
    def compress(self):
        os.system("/usr/bin/lame %s %s 2>&1 > /dev/null" % (self.wavname, self.mp3name))


if __name__ == "__main__":
    import time
    pygame.init()
    pygame.mixer.init()
    recorder = WavRecord("test.wav")
    recorder.start()
    for i in range(0,5):
        print i
        time.sleep(1)
    recorder.stop()
    recorder = None
