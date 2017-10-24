#!/usr/bin/env python


import RPi.GPIO as GPIO
import time
import os
import signal
import atexit
import requests


def move(X,Y):
    atexit.register(GPIO.cleanup)

    servopinX = 21
    servopinY = 20
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servopinX, GPIO.OUT, initial=False)
    pX = GPIO.PWM(servopinX,50) #50HZ
    pX.start(0)

    GPIO.setup(servopinY, GPIO.OUT, initial=False)
    pY = GPIO.PWM(servopinY,50) #50HZ
    pY.start(0)
    time.sleep(2)
    pX.ChangeDutyCycle(X)
    time.sleep(0.02)
    pX.ChangeDutyCycle(0)
    time.sleep(0.2)

    pY.ChangeDutyCycle(Y)
    time.sleep(0.02)
    pY.ChangeDutyCycle(0)
    time.sleep(0.2)




url = "http://127.0.0.1:8080/api/live"
c_X = 90
c_Y = 90
c_stat = "on"
while 1:
    data = {"X": c_X, "Y": c_Y, "stat": c_stat, "source": "D"}
    r = requests.post(url, data)
    try:
        X = r.json()["X"]
        Y = r.json()["Y"]
        stat = r.json()["stat"]

        if stat == "on" and stat != c_stat:
            os.system(
                "raspivid -t 0 -w 320 -h 240 -o - | ffmpeg -i - -s 320x240  -vcodec libx264 -preset:v ultrafast -f flv  rtmp://47.94.246.161:1935/hls/pet")
            print "turnon"
        if stat == "off" and stat != c_stat:
            ffmpegPID = os.popen('pgrep -lo ffmpeg').readlines()
            raspividPID = os.popen('pgrep -lo raspivid').readlines()
            if len(ffmpegPID)>0 and len(raspividPID)>0:
                ffmpegPID = ffmpegPID.split(" ")[0]
                raspividPID = raspividPID.split(" ")[0]
                os.system("kill %s"%ffmpegPID)
                os.system("kill %s" % raspividPID)
                print "shutdown"
        move(int(X),int(Y))
        #
        c_X = X
        c_Y = Y
        c_stat = stat
    except:
        pass


