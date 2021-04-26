from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.lang.builder import Builder

import serial
import serial.tools.list_ports
import os       # list files in directory to find .kv files

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
    def update(self, pitch, roll, slip, heading, headingBug):
        self.horizon.update(pitch, roll, slip)       # Pitch [deg], Roll [deg] and Slip
        self.compass.update(heading, headingBug)       # Heading [deg], HeadingBug [deg]

# ========================================================================================================================
# MAIN APP LOGIC BEGINS HERE
# ========================================================================================================================

class PfdApp(App):
    def build(self):
        """
        Runs once, sets up the variables and the app
        """
        Builder.load_file('horizon.kv')         # Load external .kv files
        Builder.load_file('compass.kv')
        Builder.load_file('bugbutton.kv')
        Builder.load_file('bugsettings.kv')

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

        self.headingBugOut = 0  #   Internal variables that will get sent out to the main computer.
        self.altBugOut = 0      #   Positions of the bugs are set based of values coming through the serial link.
        self.spdBugOut = 0      #
        self.vsiBugOut = 0      #

        self.groundTrack = 0    # [°]
        # --------------------------------------------------------------------------------------------

        self.pfd = PFD()
        self.setBugButtonLabels()
        self.openPort()
        Clock.schedule_interval(self.updateDisplayElements, 1.0 / 60.0)
        Clock.schedule_interval(self.serialReadValues, 1/50)        # Working value obtained mostly by trial and error
        return self.pfd

    def setBugButtonLabels(self):
        self.pfd.bugselectors.setHeadingFunction('Heading')
        self.pfd.bugselectors.setSpeedFunction('Speed')
        self.pfd.bugselectors.setAltFunction('ALT')
        self.pfd.bugselectors.setVsiFunction('VSI')

    def updateDisplayElements(self, dt):
        self.pfd.update(self.pitch, self.roll, self.slip, self.heading, self.headingBug)
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


    def serialReadValues(self, dt):
        try:
            serRead = self.ser.readline().decode('utf-8')       # Read line, make string ('utf-8')
            list_Str = serRead.split(';')                       # Put values in list

            if len(list_Str) == 5:
                self.pitch = float(list_Str[0])                            # Update class instance values
                self.roll = float(list_Str[1])
                self.slip = float(list_Str[2])
                self.heading = float(list_Str[3])
#                 self.headingBug = float(list_Str[4])
            if len(list_Str) < 5:
                print(f'Less than 5 values received: {serRead}')
            if len(list_Str) > 5:
                print(f'More than 5 values received: {serRead}')

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
            print('failed to read serial line')

    # def serialReadValuesContinuous(self):       # Run in separate thread or schedule!!!
    #     inputString = ''
    #     while 1
    #         serInput = self.ser.readline()
    #         inputString += serInput
    #         if inputString.count('\n') > 2:
    #             list_str

    def autoSelectPort(self):
        # Zoekt tussen de seriele poorten naar een poort die in de beschrijving het keyword heeft staan.
        keyword = 'UART'

        for p in serial.tools.list_ports.comports():
            # print(p)
            if keyword in p.description:
                print(f'Found port {p.device}')
                return p.device

        print(f'No ports automatically found, falling back to /dev/ttyS0')   # Prints if no keyword has been found
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
                    self.headingBug -= self.LfineInc
                    if self.headingBug < 0:
                        self.headingBug += 360
                elif self.pfd.bugselectors.hdgORspd == 'spd':
                    self.spdBug -= self.LfineInc
                    if self.spdBug < 0:
                        self.spdBug = 0

            if value > 0: # CW
                if self.pfd.bugselectors.hdgORspd == 'hdg':
                    self.headingBug += self.LfineInc
                    if self.headingBug > 360:
                        self.headingBug -= 360
                elif self.pfd.bugselectors.hdgORspd == 'spd':
                    self.spdBug += self.LfineInc


        if abs(value) == 2:     # Left coarse encoder
            if value < 0: # CCW
                if self.pfd.bugselectors.hdgORspd == 'hdg':
                    self.headingBug -= self.LcoarseInc
                    if self.headingBug < 0:
                        self.headingBug += 360
                elif self.pfd.bugselectors.hdgORspd == 'spd':
                    self.spdBug -= self.LcoarseInc
                    if self.spdBug < 0:
                        self.spdBug = 0

            if value > 0: # CW
                if self.pfd.bugselectors.hdgORspd == 'hdg':
                    self.headingBug += self.LcoarseInc
                    if self.headingBug > 360:
                        self.headingBug -= 360
                elif self.pfd.bugselectors.hdgORspd == 'spd':
                    self.spdBug += self.LcoarseInc

        if abs(value) == 3:     # Right fine encoder
            if value < 0: # CCW
                if self.pfd.bugselectors.altORvsi == 'alt':
                    self.altBug -= self.RfineInc * 25           # Faster movement through altitude
                    if self.altBug < 0:
                        self.altBug = 0
                elif self.pfd.bugselectors.altORvsi == 'vsi':
                    self.vsiBug -= self.RfineInc
            if value > 0: # CW
                if self.pfd.bugselectors.altORvsi == 'alt':
                    self.altBug += self.RfineInc * 25          # Faster movement through altitude
                elif self.pfd.bugselectors.altORvsi == 'vsi':
                    self.vsiBug += self.RfineInc

        if abs(value) == 4:     # Right coarse encoder
            if value < 0: # CCW
                if self.pfd.bugselectors.altORvsi == 'alt':
                    self.altBug -= self.RcoarseInc * 100           # Faster movement through altitude
                    if self.altBug < 0:
                        self.altBug = 0
                elif self.pfd.bugselectors.altORvsi == 'vsi':
                    self.vsiBug -= self.RcoarseInc
            if value > 0: # CW
                if self.pfd.bugselectors.altORvsi == 'alt':
                    self.altBug += self.RcoarseInc * 100          # Faster movement through altitude
                elif self.pfd.bugselectors.altORvsi == 'vsi':
                    self.vsiBug += self.RcoarseInc


# =======================================================================================================================
def main():
    PfdApp().run()


if __name__ == '__main__':
    main()