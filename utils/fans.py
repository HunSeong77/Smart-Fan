from RPi import GPIO
import pigpio
import time
import random
GPIO.setmode(GPIO.BCM)
pig = pigpio.pi()

class Fan:
    speedList = ['off', 'slow', 'medium', 'fast', 'natural']
    updownList = ['stop', 'up', 'down', 'auto-up', 'auto-down']
    leftRightList = ['stop', 'left', 'right', 'auto-left', 'auto-right']

    def __init__(self, servoVPin, servoHPin, speedPin, APin, BPin):
        GPIO.setup(servoHPin, GPIO.OUT)
        GPIO.setup(speedPin, GPIO.OUT)
        GPIO.setup(APin, GPIO.OUT)
        GPIO.setup(BPin, GPIO.OUT)
        self.enable = False
        self.servoVPin = servoVPin
        self.servoHPin = servoHPin
        self.Vpos = 1610
        self.Vstep = 20
        self.Hpos = 1500
        self.Hstep = 10
        self.minVpos = 1200
        self.maxVpos = 1800
        self.minHpos = 1200
        self.maxHpos = 1800
        pig.set_servo_pulsewidth(servoVPin, self.Vpos)
        pig.set_servo_pulsewidth(servoHPin, self.Hpos)
        self.natural_speed = 50
        self.natural_update_time = 0
        self.speed = GPIO.PWM(speedPin, 50)
        self.speed.start(0)
        GPIO.output(APin, GPIO.HIGH)
        GPIO.output(BPin, GPIO.LOW)

        self.state = [0, 0, 0]
        self.state_str = self.speedList[self.state[0]] + ", " + \
              self.updownList[self.state[1]] + ", " + \
            self.leftRightList[self.state[2]]

    def control(self, gesture):
        if gesture == 'None' :
            self.state[1] = 0 if self.state[1] == 1 or self.state[1] == 2 else self.state[1]
            self.state[2] = 0 if self.state[2] == 1 or self.state[2] == 2 else self.state[2]
        elif gesture == 'Fist':
            self.state[0] = 0
            self.enable = False
        elif gesture == 'One':
            self.state[0] = 1
            self.enable = True
        elif gesture == 'Two':
            self.state[0] = 2
            self.enable = True
        elif gesture == 'Three':
            self.state[0] = 3
            self.enable = True
        elif gesture == 'HighFive':
            self.state[0] = 4
            self.enable = True
        elif gesture == 'UpArrow':
            self.state[1] = 1 if self.Vpos < self.maxVpos else 0
        elif gesture == 'DownArrow':
            self.state[1] = 2 if self.Vpos > self.minVpos else 0
        elif gesture == 'LeftArrow':
            self.state[2] = 1 if self.Hpos < self.maxHpos else 0
        elif gesture == 'RightArrow':
            self.state[2] = 2 if self.Hpos > self.minHpos else 0
        elif gesture == 'UpTripleArrow':
            self.state[1] = 3
        elif gesture == 'DownTripleArrow':
            self.state[1] = 4
        elif gesture == 'LeftTripleArrow':
            self.state[2] = 3
        elif gesture == 'RightTripleArrow':
            self.state[2] = 4
        elif gesture == 'ThumbUp' :
            self.state[1] = 3
            self.state[2] = 3
        elif gesture == 'ThumbDown' :
            self.state[1] = 0
            self.state[2] = 0
        elif gesture == 'Salute' :
            self.setNeutral(20)
        self.update()

    def setNeutral(self, step):
        self.setVPos(1610, step)
        self.setHPos(1500, step)

    def setVPos(self, pos, step):
        self.state[1] = 0
        while self.Vpos > pos:
            self.Vpos = max(self.Vpos-step, pos)
            pig.set_servo_pulsewidth(self.servoVPin, self.Vpos)
            time.sleep(0.1)
        while self.Vpos < pos:
            self.Vpos = min(self.Vpos + step, pos)
            pig.set_servo_pulsewidth(self.servoVPin, self.Vpos)
            time.sleep(0.1)

    def setHPos(self, pos, step):
        self.state[2] = 0
        while self.Hpos > pos:
            self.Hpos = max(self.Hpos-step, pos)
            pig.set_servo_pulsewidth(self.servoHPin, self.Hpos)
            time.sleep(0.1)
        while self.Hpos < pos:
            self.Hpos = min(self.Hpos + step, pos)
            pig.set_servo_pulsewidth(self.servoHPin, self.Hpos)
            time.sleep(0.1)

    def update(self):
        if self.enable:
            if self.state[1] == 1: self.Vpos += self.Vstep  # up
            elif self.state[1] == 2: self.Vpos -= self.Vstep # down
            elif self.state[1] == 3: # auto-up
                if self.Vpos < self.maxVpos : self.Vpos += self.Vstep
                else : self.state[1] = 4
            elif self.state[1] == 4: # auto-down
                if self.Vpos > self.minVpos : self.Vpos -= self.Vstep
                else : self.state[1] = 3
            if self.state[2] == 1: self.Hpos += self.Hstep
            elif self.state[2] == 2: self.Hpos -= self.Hstep
            elif self.state[2] == 3: # auto-left
                if self.Hpos < self.maxHpos : self.Hpos += self.Hstep
                else : self.state[2] = 4
            elif self.state[2] == 4: # auto-right
                if self.Hpos > self.minHpos : self.Hpos -= self.Hstep
                else : self.state[2] = 3
            pig.set_servo_pulsewidth(self.servoVPin, self.Vpos)
            pig.set_servo_pulsewidth(self.servoHPin, self.Hpos)
        if self.state[0] == 4:
            if time.time() - self.natural_update_time >= 2:
                self.natural_update_time = time.time()
                self.natural_speed = self.natural_speed + random.randint(-30, 30)
                if self.natural_speed < 0 : self.natural_speed = 0
                if self.natural_speed > 90 : self.natural_speed = 90
                self.speed.ChangeDutyCycle(self.natural_speed)
        else :
            self.speed.ChangeDutyCycle(self.state[0] * 30)

        self.state_str = self.speedList[self.state[0]] + ", " +\
            self.updownList[self.state[1]] + ", " + \
            self.leftRightList[self.state[2]]
        
    def get_state_str(self):
        return self.state_str
    
    def __del__(self):
        self.setNeutral(10)
        GPIO.cleanup()