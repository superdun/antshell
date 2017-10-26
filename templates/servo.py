#!/usr/bin/env python


import RPi.GPIO as GPIO
import time
import os
import signal
import atexit
import requests
from subprocess import *

def move(pX,pY,X,Y):
    print "moving"
    pX.ChangeDutyCycle(2.5 + 10 * X / 180)
    time.sleep(1)
    pX.ChangeDutyCycle(0)
    time.sleep(0.2)
    pY.ChangeDutyCycle(2.5 + 10 * Y/ 180)
    time.sleep(1)
    pY.ChangeDutyCycle(0)
    time.sleep(0.2)
    print "move to %d,%d"%(X,Y)



url = "http://ant-shell.com/api/live"
c_X = 90
c_Y = 90
c_stat = "on"
atexit.register(GPIO.cleanup)

servopinX = 21
servopinY = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(servopinX, GPIO.OUT, initial=False)
pX = GPIO.PWM(servopinX, 50)  # 50HZ
pX.start(0)

GPIO.setup(servopinY, GPIO.OUT, initial=False)
pY = GPIO.PWM(servopinY, 50)  # 50HZ
pY.start(0)
time.sleep(2)
p1=""
p2=""
print "starting"
while 1:
    time.sleep(1)
    try :
        data = {"X": c_X, "Y": c_Y, "stat": c_stat, "source": "D"}
        r = requests.post(url, data)
        print r.json()

        X = r.json()["X"]
        Y = r.json()["Y"]
        stat = r.json()["stat"]

        if stat == "on" and stat != c_stat:
            print "on...."
            p1 = Popen(['raspivid', '-t', '0', '-w', '320', '-h', '240', '-o', '-'], stdout=PIPE)
            p2 = Popen(
                ['ffmpeg', '-i', '-', '-s', '320x240', '-vcodec', 'libx264', '-preset:v', 'ultrafast', '-f', 'flv',
                 'rtmp://47.94.246.161:1935/hls/pet']
                , stdin=p1.stdout, stdout=None)
            print "turnon"
        if stat == "off" and stat != c_stat:
            ffmpegPID = os.popen('pgrep -lo ffmpeg').readlines()
            raspividPID = os.popen('pgrep -lo raspivid').readlines()
            if len(ffmpegPID) > 0 and len(raspividPID) > 0 and p1 and p2:
                p1.kill()
                p2.kill()
                # ffmpegPID = ffmpegPID[0].split(" ")
                # raspividPID = raspividPID[0].split(" ")
                # os.system("kill %s" % ffmpegPID)
                # os.system("kill %s" % raspividPID)
                print "shutdown live"
        if c_X != X or c_Y != Y:
            move(pX, pY, int(X), int(Y))
        #
        c_X = X
        c_Y = Y
        c_stat = stat
    except:
        print "err"




