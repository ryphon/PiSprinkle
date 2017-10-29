#!/bin/python

# import RPi.GPIO as GPIO
import time
# GPIO.setmode(GPIO.BCM)

zones = []
zoneNums = [4, 10, 27, 22, 5, 6]


class Zone:
    '''
    Controller for a sprinkler zone
    '''

    def __init__(self, pinNum: int):
        self.pinNum = pinNum
        self.running = False
#         GPIO.setup(pinNum, GPIO.OUT)
#         GPIO.output(pinNum, GPIO.LOW)

    def run(self):
#         GPIO.output(self.pinNum, GPIO.HIGH)
        self.running = True

    def stop(self):
#         GPIO.output(self.pinNum, GPIO.LOW)
        self.running = False

    def is_running(self):
#         return GPIO.HIGH == GPIO.input(self.pinNum)
        return self.running


for zone in zoneNums:
    zones.append(Zone(zone))
