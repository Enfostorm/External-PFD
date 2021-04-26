

'''
Klasse die bij een overgang van de staat een callback kan aanroepen, en zijn waarde teruggeeft.

12/3/2021 PvdT
pull_up_down veranderd naar UPD_UP om COM met GND te kunnen verbinden, minder kans op schade
    bij foute verbinding (5V op GPIO)
'''

'''
00 --> 01    R1
11 --> 10    R1
'''
import RPi.GPIO as GPIO

class Encoder:

    def __init__(self, leftPin, rightPin, returnValue, callback=None):
        self.leftPin = leftPin
        self.rightPin = rightPin
        self.state = '00'
        self.returnValue = returnValue
        self.direction = None
        self.callback = callback
        GPIO.setup(self.leftPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)          # changed to PUD.UP
        GPIO.setup(self.rightPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)         # changed to PUD.UP
        GPIO.add_event_detect(self.leftPin, GPIO.BOTH, callback=self.transitionOccurred)  # Setup callbacks for detection of pinstate changes
        GPIO.add_event_detect(self.rightPin, GPIO.BOTH, callback=self.transitionOccurred)

    def transitionOccurred(self, channel):
        p1 = GPIO.input(self.leftPin)
        p2 = GPIO.input(self.rightPin)
        newState = "{}{}".format(p1, p2)
        
        if self.state == '00':
            if newState == '01': # halve klik naar rechts
                self.direction = 'R'
            if newState == '10': # halve klik naar rechts
                self.direction = 'L'
                
        if self.state == '11':
            if newState == '10': # halve klik naar rechts
                self.direction == 'R'
            if newState == '01': # halve klik naar links
                self.direction == 'L'
        
        if self.state == '01':
            if newState == '11': # is een halve klik naar rechts verplaatst
                if self.direction == 'R': # controle of de vorige klik in dezelfde richting was
                    if self.callback is not None: # als er een callback gedefinieerd is geef de waarde van de counter terug
                        self.callback(self.returnValue)
            if newState == '00': # is een halve klik naar links verplaatst
                if self.direction == 'L': # controle of de vorige klik in dezelfde richting was
                    if self.callback is not None:
                        self.callback(-self.returnValue)
        
        if self.state == '10':
            if newState == '11': # is een halve klik naar links verplaatst
                if self.direction == 'L': # controle of de vorige klik in dezelfde richting was
                    if self.callback is not None:
                        self.callback(-self.returnValue)
                
            if newState == '00': # is een halve klik naar rechts verplaatst
                if self.direction == 'R': # controle of de vorige klik in dezelfde richting was
                    if self.callback is not None:
                        self.callback(self.returnValue)
        
        self.state = newState

