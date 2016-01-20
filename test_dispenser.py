#!/usr/bin/env python

import serial
import os
import time

if __name__ == '__main__':
        ser = serial.Serial("/dev/ttyUSB0",19200,timeout=2)
        ser.close()
        ser.open()
        time.time(0.1);
        ON=bytearray([0x02,0x01,0x80,0x00,0x03,0x80])
        ser.write(ON)
        ser.flush()       
        
        read_val  = ser.read(size=64)
        print read_val   

        ser.close()
    
        #~ f = open("/dev/ttyUSB0", "wb")
        #~ f.write("020180000380".decode("hex"))
        #~ f.write("020180000380".decode("hex"))
        #~ f.flush()
        #~ f.close()
    

