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

    def update(self, pitch, roll, slip, heading, altitude, speed, headingRate, vSpeed, deltaSpeed, headingBug, altBug, spdBug, vsiBug, groundTrack, altitudeUnit, speedUnit, vSpeedUnit):
        self.horizon.update(pitch, roll, slip)       # Pitch [deg], Roll [deg] and Slip
        self.compass.update(heading, headingBug)       # Heading [deg], HeadingBug [deg]
        self.bugselectors.updateValues(headingBug, altBug, spdBug, vsiBug, altitudeUnit, speedUnit, vSpeedUnit)

# ========================================================================================================================
# MAIN APP LOGIC BEGINS HERE
# ========================================================================================================================

class PfdApp(App):
    def build(self):
        Config.set('graphics', 'fullscreen', 'auto')
        Config.set('graphics', 'show_cursor', '0')
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

        self.serialDebug = False     # Print the incoming serial datastream in console
        # --------------------------------------------------------------------------------------------
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
        self.deltaSpeed = 0     #        # Change in speed / s

        self.headingBug = 0     # [°]    # Bugvalues
        self.altBug = 0         # [altitudeUnit]
        self.spdBug = 0         #
        self.vsiBug = 0         #

        self.headingBugOut = 0  #   Internal variables that will get sent out to the main computer over serial.
        self.altBugOut = 0      #   Positions of the bugs are set based off of values coming back through the serial link.
        self.spdBugOut = 0      #
        self.vsiBugOut = 0      #

        self.groundTrack = 0    # [°]
        # --------------------------------------------------------------------------------------------

        self.pfd = PFD()
        self.setBugButtonLabels()
        self.openPort()
        Clock.schedule_interval(self.updateDisplayElements, 1.0 / 60.0)
        threading.Thread(target=self.serialReadValuesThread, daemon=True).start()        # Separate thread to read the serial input. Daemon makes sure the thread closes if the main program closes
        Clock.schedule_interval(self.serialWriteValues, 1/30)
        return self.pfd

    def setBugButtonLabels(self):
        self.pfd.bugselectors.setHeadingFunction('Heading')
        self.pfd.bugselectors.setSpeedFunction('Speed')
        self.pfd.bugselectors.setAltFunction('ALT')
        self.pfd.bugselectors.setVsiFunction('VSI')

    def updateDisplayElements(self, dt):
        self.pfd.update(self.pitch, self.roll, self.slip, self.heading, self.altitude, self.speed,
                        self.headingRate, self.vSpeed, self.deltaSpeed,
                        self.headingBug, self.altBug, self.spdBug, self.vsiBug,
                        self.groundTrack,
                        self.altitudeUnit, self.speedUnit, self.vSpeedUnit)
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
        # Only run this method in a separate thread or your program will get stuck in an infinite loop!!
        expected_length = 14
        while True:
            try:
                print('beginning serial read')
                serRead = self.ser.readline().decode('utf-8')       # Read line, make string ('utf-8')
                list_Str = serRead.split(';')                       # Put values in list

                if len(list_Str) == expected_length:
                    self.pitch = float(list_Str[0])                            # Update app values
                    self.roll = float(list_Str[1])
                    self.slip = float(list_Str[2])
                    self.heading = float(list_Str[3])
                    self.altitude = float(list_Str[4])
                    self.speed = float(list_Str[5])

                    self.headingRate = float(list_Str[6])
                    self.vSpeed = float(list_Str[7])
                    self.deltaSpeed = float(list_Str[8])

                    self.headingBug = float(list_Str[9])
                    self.altBug = float(list_Str[10])
                    self.spdBug = float(list_Str[11])
                    self.vsiBug = float(list_Str[12])

                    self.groundTrack = float(list_Str[13])
                if len(list_Str) < expected_length:
                    print(f'Less than {expected_length} values received: {serRead}')
                if len(list_Str) > expected_length:
                    print(f'More than {expected_length} values received: {serRead}')
                    
                if self.serialDebug:
                    print("-----------------")
                    print("Serial input   : ", serRead)
                    print("Serial List    : ", list_Str)
                    print("-----------------")
                    print("Pitch          : ", self.pitch)
                    print("Roll           : ", self.roll)
                    print("Slip           : ", self.slip)
                    print("Heading        : ", self.heading)
                    print("HeadingBug     : ", self.headingBug)
                    print("-----------------")
                    print("                 ")
            except:
                print('Error while reading serial values')
                time.sleep(1)
            
    def serialWriteValues(self, dt):
        valueList = [self.headingBugOut, self.altBugOut, self.spdBugOut, self.vsiBugOut]
        self.ser.write(self.strForSerialOut(valueList).encode())
        
    def strForSerialOut(self, valueList):
        # Takes a list of arguments, rounds them to 4 numbers after the comma, and joins them together in a string that can be sent through a serial link.
        # The outputstring still needs to be encoded into bytes (with strForSerialOut(valueList).encode() for example).
        strVariables = [self.roundedStr(element, 4) for element in valueList]
        dataString = ';'.join(strVariables)
        stringToWrite = dataString + '\n'
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
    
    # ________________________________________________________________________________________________
    # Encoder methods

    def encoderUpdate(self, value):     # Gets called by Encoder class as callback
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
                    self.headingBugOut -= self.LfineInc
                    if self.headingBugOut < 0:
                        self.headingBugOut += 360
                elif self.pfd.bugselectors.hdgORspd == 'spd':
                    self.spdBugOut -= self.LfineInc
                    if self.spdBugOut < 0:
                        self.spdBugOut = 0

            if value > 0: # CW
                if self.pfd.bugselectors.hdgORspd == 'hdg':
                    self.headingBugOut += self.LfineInc
                    if self.headingBugOut >= 360:
                        self.headingBugOut -= 360
                elif self.pfd.bugselectors.hdgORspd == 'spd':
                    self.spdBugOut += self.LfineInc


        if abs(value) == 2:     # Left coarse encoder
            if value < 0: # CCW
                if self.pfd.bugselectors.hdgORspd == 'hdg':
                    self.headingBugOut -= self.LcoarseInc
                    if self.headingBugOut < 0:
                        self.headingBugOut += 360
                elif self.pfd.bugselectors.hdgORspd == 'spd':
                    self.spdBugOut -= self.LcoarseInc
                    if self.spdBugOut < 0:
                        self.spdBugOut = 0

            if value > 0: # CW
                if self.pfd.bugselectors.hdgORspd == 'hdg':
                    self.headingBugOut += self.LcoarseInc
                    if self.headingBugOut > 360:
                        self.headingBugOut -= 360
                elif self.pfd.bugselectors.hdgORspd == 'spd':
                    self.spdBugOut += self.LcoarseInc

        if abs(value) == 3:     # Right fine encoder
            if value < 0: # CCW
                if self.pfd.bugselectors.altORvsi == 'alt':
                    self.altBugOut -= self.RfineInc * 100           # Faster movement through altitude
                    if self.altBugOut < 0:
                        self.altBugOut = 0
                elif self.pfd.bugselectors.altORvsi == 'vsi':
                    self.vsiBugOut -= self.RfineInc
            if value > 0: # CW
                if self.pfd.bugselectors.altORvsi == 'alt':
                    self.altBugOut += self.RfineInc * 100          # Faster movement through altitude
                elif self.pfd.bugselectors.altORvsi == 'vsi':
                    self.vsiBugOut += self.RfineInc

        if abs(value) == 4:     # Right coarse encoder
            if value < 0: # CCW
                if self.pfd.bugselectors.altORvsi == 'alt':
                    self.altBugOut -= self.RcoarseInc * 100           # Faster movement through altitude
                    if self.altBugOut < 0:
                        self.altBugOut = 0
                elif self.pfd.bugselectors.altORvsi == 'vsi':
                    self.vsiBugOut -= self.RcoarseInc
            if value > 0: # CW
                if self.pfd.bugselectors.altORvsi == 'alt':
                    self.altBugOut += self.RcoarseInc * 100          # Faster movement through altitude
                elif self.pfd.bugselectors.altORvsi == 'vsi':
                    self.vsiBugOut += self.RcoarseInc


# =======================================================================================================================
def main():
    PfdApp().run()


if __name__ == '__main__':
    main()