import os
import time
import RPi.GPIO as GPIO
import pyttsx

def shutdown(channel):
    logfile = open('singing_plants.log', 'a')
    logfile.write(str(time.time()) + " shutting down\n")
    logfile.close()
    engine = pyttsx.init()
    engine.say('System Offline')
    engine.runAndWait()
    print 'shutting down'
    os.system('sudo shutdown -h now')

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(6, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(12, GPIO.OUT)
    GPIO.add_event_detect(6, GPIO.FALLING, callback = shutdown, bouncetime = 2000)
    GPIO.output(12, GPIO.HIGH)

setup()
while 1:
    time.sleep(1)
