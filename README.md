dialastory
==========

Dial A Story



**Install & Setup**

    sudo apt-get install python-serial
    sudo apt-get install python-paramiko
    sudo apt-get install lame mpg123


Install latest PyAudio:

    $ sudo apt-get install git
    $ sudo git clone http://people.csail.mit.edu/hubert/git/pyaudio.git
    $ sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
    $ sudo apt-get install python-dev
    $ cd pyaudio
    $ sudo python setup.py install
    
Update to latest firmware:

    sudo rpi-config
    
Add

    options snd-usb-audio index=0
to /etc/modprobe.d/alsa-base.conf


Add 

    dwc_otg.fiq_fsm_enable=0
    smsc95xx.turbo_mode=N
to /boot/cmdline.txt


Enter the cron/ directory and do the following:

    sudo crontab penguinphone
    
    
Copy utils/99-puffin.rules to 

    /etc/udev/rules.d/
and edit to replace dispenser ids
    


