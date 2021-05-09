from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.config import Config

import serial
import serial.tools.list_ports
import os       # list files in directory to find .kv files

import threading
import time

from horizon import HorizonEverything
from bugbutton import BugButton
from compass import CompassEverything
from bugsettings import BugSelectors
from encoder import Encoder
import RPi.GPIO as GPIO


class PFD(Widget):
    horizon = ObjectProperty()
    compass = ObjectProperty()
    bugselectors = ObjectProperty()

    def update(self, serialReadSuccess, pitch, roll, slip, heading, altitude, speed, headingRate, vSpeed, deltaSpeed, headingBug, altBug, spdBug, vsiBug, groundTrack, altitudeUnit, speedUnit, vSpeedUnit, headingBugTemp, altBugTemp, spdBugTemp, vsiBugTemp):
        self.horizon.update(pitch, roll, slip)       # Pitch [deg], Roll [deg] and Slip
        self.compass.update(heading, headingBug, headingRate, groundTrack)       # Heading [deg], HeadingBug [deg]
        self.bugselectors.updateValues(headingBugTemp, spdBugTemp, altBugTemp, vsiBugTemp, speedUnit, altitudeUnit, vSpeedUnit)

class ErrorCross(Widget):
    pass
# ========================================================================================================================
# MAIN APP LOGIC BEGINS HERE
# ========================================================================================================================

class PfdApp(App):
    def build(self):
        Config.set('graphics', 'fullscreen', 'auto')
        Config.set('graphics', 'show_cursor', '0')
        Config.set('graphics', 'multisamples', '0')
        """
        Runs once, sets up the variables and the app
        """
        self.load_kv('horizon.kv')         # Load external .kv files
        self.load_kv('compass.kv')
        self.load_kv('bugbutton.kv')
        self.load_kv('bugsettings.kv')

        GPIO.setmode(GPIO.BOARD)
        Encoder(29, 31, 1, self.encoderUpdate)          # Initialize encoders:  1| Left fine
        Encoder(33, 35, 2, self.encoderUpdate)          #                       2| Left coarse
        Encoder(11, 13, 3, self.encoderUpdate)          #                       3| Right fine
        Encoder(15, 19, 4, self.encoderUpdate)          #                       4| Right coarse

        LBTN = 37                                       # Setup pushbuttons
        RBTN = 21
        buttonPinList = [LBTN, RBTN]
        GPIO.setup(buttonPinList, GPIO.IN, pull_up_down = GPIO.PUD_UP)  # Pins for pushbuttons as active low
        GPIO.add_event_detect(LBTN, GPIO.RISING, callback = self.confirmBugsLeft)
        GPIO.add_event_detect(RBTN, GPIO.RISING, callback = self.confirmBugsRight)

        self.serialDebug = False     # Print the incoming serial datastream in console
        self.serialReadSuccess = False
        self.serReadErrorCounter = 0
        self.errorCrossActive = False
        self.serialReadErrorMessage = ''
        self.errorCross = ErrorCross()
        # ------------------------------------    VARIABLES    ----------------------------------------
        self.pitch = 0          # [°]        # Setup variables for the app
        self.roll = 0           # [°]
        self.slip = 0           # [°]
        self.heading = 0        # [°]
        self.altitude = 0       # [altitudeUnit]
        self.speed = 0          #

        self.altitudeUnit = ''  #
        self.speedUnit = ''     #
        self.vSpeedUnit = ''    #

        self.headingRate = 0    # [°/s]
        self.vSpeed = 0         #
        self.deltaSpeed = 0     #        # Change in speed / s (acceleration)

        self.headingBug = 0     # [°]    # Bugvalues
        self.altBug = 0         # [altitudeUnit]
        self.spdBug = 0         #
        self.vsiBug = 0         #

        self.headingBugOut = 0  #   Internal variables that will get sent out to the main computer over serial.
        self.altBugOut = 0      #   Positions of the bugs are set based off of values coming back through the serial link.
        self.spdBugOut = 0      #
        self.vsiBugOut = 0      #

        self.groundTrack = 0    # [°]

        self.headingBugTemp = 0 # Values displayed in the bugButtons before they are confirmed by a press of the button.
        self.altBugTemp = 0     #
        self.spdBugTemp = 0     #
        self.vsiBugTemp = 0     #
        # --------------------------------------------------------------------------------------------

        self.pfd = PFD()
        self.setBugButtonLabels()
        self.openPort()
        self.ser.flushInput()               # Makes sure fresh values are read so there's no need to catch up with old values from the buffer
        self.ser.flushOutput()
        Clock.schedule_interval(self.updateDisplayElements, 1/60)
        threading.Thread(target=self.serialReadValuesThread, daemon=True).start()       # Separate thread to read the serial input. Daemon makes sure the thread closes if the main program closes
                                                                                        #          This is will NOT use a different core, but will be able to execute alongside the main program see documentation for more information
        Clock.schedule_interval(self.serialWriteValues, 1/60)
        Clock.schedule_interval(self.checkConnectivity, 1/5)                            # Decide if red cross should be shown on screen
        return self.pfd

    def setBugButtonLabels(self):
        self.pfd.bugselectors.setHeadingFunction('Heading')
        self.pfd.bugselectors.setSpeedFunction('Speed')
        self.pfd.bugselectors.setAltFunction('ALT')
        self.pfd.bugselectors.setVsiFunction('VSI')

    def updateDisplayElements(self, dt):
        self.pfd.update(self.serialReadSuccess, self.pitch, self.roll, self.slip, self.heading, self.altitude, self.speed,
                        self.headingRate, self.vSpeed, self.deltaSpeed,
                        self.headingBug, self.altBug, self.spdBug, self.vsiBug,
                        self.groundTrack,
                        self.altitudeUnit, self.speedUnit, self.vSpeedUnit,
                        self.headingBugTemp, self.altBugTemp, self.spdBugTemp, self.vsiBugTemp)

    # ________________________________________________________________________________________________
    # Serial data methods

    def openPort(self):       
        self.port = self.autoSelectPort()
        self.BAUD = 115200
        try:
            self.ser = serial.Serial(port = self.port,                      # Setup serial connection
                                baudrate = self.BAUD,
                                parity = serial.PARITY_NONE,
                                stopbits = serial.STOPBITS_ONE,
                                bytesize = serial.EIGHTBITS,
                                timeout = 1)
        except:
            print('failed to find suitable port')
    
    def serialReadValuesThread(self):
        # !!!Only run this method in a separate thread or your program will get stuck in an infinite loop blocking all other methods!!!
        
        expected_length = 15 + 1     # Amount of parameters that get transmitted, +1 for the \n
        
        if self.serialReadSuccess == False:     # Prevent data from piling up while time-out is in progress
            self.ser.flushInput()               # 
            self.ser.readline()                 # Discard first line of new data so new readLine is a full line (flushInput does not remove full lines.)

        print('readThread started')
        while True:
            try:
                list_Str = ['']
                serRead = self.ser.readline().decode('utf-8')       # Read line, make string ('utf-8')
                list_Str = serRead.split(';')                       # Put values in list

                if len(list_Str) == expected_length:                                                # "Correct" path
                    self.pitch = float(list_Str[0])                            # Update app values
                    self.roll = float(list_Str[1])
                    self.slip = float(list_Str[2])
                    self.heading = float(list_Str[3])
                    self.altitude = float(list_Str[4])
                    self.speed = float(list_Str[5])

                    self.headingRate = float(list_Str[6])
                    self.vSpeed = float(list_Str[7])

                    self.headingBug = float(list_Str[8])
                    self.altBug = float(list_Str[9])
                    self.spdBug = float(list_Str[10])
                    self.vsiBug = float(list_Str[11])

                    self.groundTrack = float(list_Str[12])

                    self.altitudeUnit = str(list_Str[13])
                    self.speedUnit = str(list_Str[14])

                    self.serialReadSuccess = True       # If it gets here, the read was a success

                if list_Str == None:
                    print('readline is empty')
                    
                if len(list_Str) < expected_length:            # Path if too little values are received
                    if 'DEVICE' in serRead:
                        self.answerQuery()
                        print('Answered query from main device.')
                    else:
                        print(f'Less than {expected_length} values received: {serRead}')
                        self.serialReadSuccess = False
                        self.serialReadErrorMessage = f'Not enough variables in the read line: expected {expected_length} values but received {len(list_Str)}'

                if len(list_Str) > expected_length:                                                 # Path if more values than expected are received.
                    print(f'More than {expected_length} values received: {serRead}')
                    self.serialReadSuccess = False
                    self.serialReadErrorMessage = f'Too much variables in the read line: expected {expected_length} values but received {len(list_Str)}'

                    
                if self.serialDebug:
                    for item in list_Str:
                        print(float(item))

            except Exception as e:

                self.serialReadSuccess = False
                self.serialReadErrorMessage = 'serialReadValuesThread exception: Failed to read serial line.'
                print(repr(e) + '\n')

    def answerQuery(self):
        self.ser.write('PFD\n'.encode())
            
    def serialWriteValues(self, dt):
        # Return the bugValues from the PFD to the main computer once communication has been established.
        # Nothing gets sent if no values have been received so the identifying string is the only thing that gets sent.
        if self.serialReadSuccess:
            valueList = [self.headingBugOut, self.altBugOut, self.spdBugOut, self.vsiBugOut]
            self.ser.write(self.strForSerialOut(valueList).encode())
        
    def strForSerialOut(self, valueList):
        # Takes a list of arguments, rounds them to 4 numbers after the comma, and joins them together in a string that can be sent through a serial link.
        # The outputstring still needs to be encoded into bytes (with strForSerialOut(valueList).encode() for example).
        strVariables = [self.roundedStr(element, 4) for element in valueList]
        dataString = ';'.join(strVariables)
        stringToWrite = dataString + ';\n'
        return stringToWrite
    
    def roundedStr(self, number, afterComma):
        # roundedStr(123,4567890, 2) ==> 123,45
        return str(round(pow(10, afterComma)*number)/pow(10, afterComma))
                

    def autoSelectPort(self):
        # Looks for a serial device which has the keyword in its description, returns the port of the first device it finds.
        #     Otherwise returns /dev/ttyS0 (default serial port for serial via GPIO on RPi)
        keyword = 'UART'
        for p in serial.tools.list_ports.comports():
            if keyword in p.description:
                print(f'Found port {p.device}')
                return p.device

        print(f'No ports with keyword {keyword} automatically found, falling back to /dev/ttyS0')   # Prints if no keyword has been found
        return '/dev/ttyS0'

    def checkConnectivity(self, dt):
        if self.serialReadSuccess:
            self.serReadErrorCounter = 0
            if self.errorCrossActive:
                self.pfd.remove_widget(self.errorCross)
                self.errorCrossActive = False

        else:
            self.serReadErrorCounter += 1
            if self.serReadErrorCounter > 0:
                if not self.errorCrossActive:
                    self.pfd.add_widget(self.errorCross)
                    self.errorCrossActive = True

        
    
    # ________________________________________________________________________________________________
    # Encoder methods

    def encoderUpdate(self, value):     # Gets called by Encoder class as callback
        # Changes the values of the bugs depending on which button is selected on the screen and which encoder is being turned.
        # The value only gets sent once the button on the encoders is pushed.
        '''
        Possible values of value:
        1 = Lfine
        2 = Lcoarse
        3 = Rfine
        4 = Rcoarse
        pos: CW click
        neg: CCW click
        '''
        # increment values
        self.LfineInc = 1
        self.LcoarseInc = 10
        self.RfineInc = 1
        self.RcoarseInc = 10

        if abs(value) == 1:     # Left fine encoder
            if value < 0: # CCW
                if self.pfd.bugselectors.hdgORspd == 'hdg':
                    self.headingBugTemp -= self.LfineInc
                    if self.headingBugTemp < 0:
                        self.headingBugTemp += 360
                elif self.pfd.bugselectors.hdgORspd == 'spd':
                    self.spdBugTemp -= self.LfineInc
                    if self.spdBugTemp < 0:
                        self.spdBugTemp = 0

            if value > 0: # CW
                if self.pfd.bugselectors.hdgORspd == 'hdg':
                    self.headingBugTemp += self.LfineInc
                    if self.headingBugTemp >= 360:
                        self.headingBugTemp -= 360
                elif self.pfd.bugselectors.hdgORspd == 'spd':
                    self.spdBugTemp += self.LfineInc


        if abs(value) == 2:     # Left coarse encoder
            if value < 0: # CCW
                if self.pfd.bugselectors.hdgORspd == 'hdg':
                    self.headingBugTemp -= self.LcoarseInc
                    if self.headingBugTemp < 0:
                        self.headingBugTemp += 360
                elif self.pfd.bugselectors.hdgORspd == 'spd':
                    self.spdBugTemp -= self.LcoarseInc
                    if self.spdBugTemp < 0:
                        self.spdBugTemp = 0

            if value > 0: # CW
                if self.pfd.bugselectors.hdgORspd == 'hdg':
                    self.headingBugTemp += self.LcoarseInc
                    if self.headingBugTemp > 360:
                        self.headingBugTemp -= 360
                elif self.pfd.bugselectors.hdgORspd == 'spd':
                    self.spdBugTemp += self.LcoarseInc

        if abs(value) == 3:     # Right fine encoder
            if value < 0: # CCW
                if self.pfd.bugselectors.altORvsi == 'alt':
                    self.altBugTemp -= self.RfineInc * 100           # Faster movement through altitude
                    if self.altBugTemp < 0:
                        self.altBugTemp = 0
                elif self.pfd.bugselectors.altORvsi == 'vsi':
                    self.vsiBugTemp -= self.RfineInc
            if value > 0: # CW
                if self.pfd.bugselectors.altORvsi == 'alt':
                    self.altBugTemp += self.RfineInc * 100          # Faster movement through altitude
                elif self.pfd.bugselectors.altORvsi == 'vsi':
                    self.vsiBugTemp += self.RfineInc

        if abs(value) == 4:     # Right coarse encoder
            if value < 0: # CCW
                if self.pfd.bugselectors.altORvsi == 'alt':
                    self.altBugTemp -= self.RcoarseInc * 100           # Faster movement through altitude
                    if self.altBugTemp < 0:
                        self.altBugTemp = 0
                elif self.pfd.bugselectors.altORvsi == 'vsi':
                    self.vsiBugTemp -= self.RcoarseInc
            if value > 0: # CW
                if self.pfd.bugselectors.altORvsi == 'alt':
                    self.altBugTemp += self.RcoarseInc * 100          # Faster movement through altitude
                elif self.pfd.bugselectors.altORvsi == 'vsi':
                    self.vsiBugTemp += self.RcoarseInc

    def confirmBugsLeft(self, dt):
        # Gets called when the left encoder is pressed
        if self.pfd.bugselectors.hdgORspd == 'hdg':
            self.headingBugOut = self.headingBugTemp
        if self.pfd.bugselectors.hdgORspd == 'spd':
            self.spdBugOut = self.spdBugTemp

    def confirmBugsRight(self, dt):
        # Gets called when the right encoder is pressed
        if self.pfd.bugselectors.altORvsi == 'alt':
            self.altBugOut = self.altBugTemp
        if self.pfd.bugselectors.altORvsi == 'vsi':
            self.vsiBugOut = self.vsiBugTemp

# =======================================================================================================================
def main():
    PfdApp().run()


if __name__ == '__main__':
    main()