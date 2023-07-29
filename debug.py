

import RPi.GPIO as GPIO 
from time import sleep   
import cv2 as cv
import numpy as np

import pigpio


GPIO.setmode(GPIO.BCM)

servoVPin = 12             
servoHPin = 7                

powerPin = 18
APin = 14
BPin = 15

pi = pigpio.pi()

pi.set_servo_pulsewidth(servoVPin, 1500)
pi.set_servo_pulsewidth(servoHPin, 1500)

GPIO.setup(powerPin, GPIO.OUT)
GPIO.setup(APin, GPIO.OUT)
GPIO.setup(BPin, GPIO.OUT)

fan = GPIO.PWM(powerPin, 50)
fan.start(50)

vduty = 1500
hduty = 1500

powerduty = 0

prev_vduty = vduty
prev_hduty = hduty
prev_powerduty = powerduty

GPIO.output(APin, GPIO.HIGH)
GPIO.output(BPin, GPIO.LOW)


print_key = 0
while True:
    key = cv.waitKey(30)
    if key == 27:
        break
    
    image = np.zeros((300, 300, 3), np.uint8)
    if key != -1:
        print_key = key
    if key == 119:
        vduty = min(vduty+10, 2300)
    elif key == 115:
        vduty = max(vduty-10, 700)
    elif key == 97:
        hduty = min(hduty+10, 2300)
    elif key == 100:
        hduty = max(hduty-10, 700)
    elif key == 101:
        powerduty = min(powerduty + 1, 100)
    elif key == 113:
        powerduty = max(powerduty - 1, 0)
    image = cv.putText(image, f"Vertical   : {vduty}%", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv.LINE_AA)
    image = cv.putText(image, f"Horizental : {hduty}%", (10, 80), cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv.LINE_AA)
    image = cv.putText(image, f"Power      : {powerduty}%", (10, 130), cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv.LINE_AA)

    image = cv.putText(image, "Up:'W', Down:'S'", (10, 210), cv.FONT_HERSHEY_SIMPLEX, 1.0, (100, 100, 100), 2, cv.LINE_AA)
    image = cv.putText(image, "Left:'A', Right:'D'", (10, 240), cv.FONT_HERSHEY_SIMPLEX, 1.0, (100, 100, 100), 2, cv.LINE_AA)
    image = cv.putText(image, "Fast:'E', Slow:'Q'", (10, 270), cv.FONT_HERSHEY_SIMPLEX, 1.0, (100, 100, 100), 2, cv.LINE_AA)

    pi.set_servo_pulsewidth(servoVPin, vduty)
    pi.set_servo_pulsewidth(servoHPin, hduty)
    fan.ChangeDutyCycle(powerduty)

    prev_vduty = vduty
    prev_hduty = hduty
    prev_powerduty = powerduty
    cv.imshow('dbg', image)

cv.destroyAllWindows()
GPIO.cleanup()