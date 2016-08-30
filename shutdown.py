import os
import time
import RPi.GPIO as GPIO

def shutdown(channel):
    print 'shutting down'
    os.system('sudo shutdown -h now')

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(5, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(13, GPIO.OUT)
    GPIO.add_event_detect(5, GPIO.FALLING, callback = shutdown, bouncetime = 2000)
    GPIO.output(13, GPIO.HIGH)

setup()
while 1:
    time.sleep(1)
