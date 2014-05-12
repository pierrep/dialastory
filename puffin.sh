#!/bin/bash
cd puffin-master
sudo stty -g -F /dev/ttyACM0 "500:5:cbd:8a3b:3:1c:7f:15:4:0:1:0:11:13:1a:0:12:f:17:16:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0"
while true; do
	sudo ./puffin.py
done
