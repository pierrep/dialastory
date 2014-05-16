#!/bin/sh
cd  /home/penguinphone/dialastory
while true; do
	./sftp.py -s 54.206.48.162 -e -w -l ./mp3s -r upload -u booth -m
done

