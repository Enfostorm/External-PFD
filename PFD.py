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


class PFD(Widget):
    horizon = ObjectProperty(None)
    compass = ObjectProperty(None)
    def update(self, pitch, roll, slip, heading, headingBug):
        self.horizon.update(pitch, roll, slip)       # Pitch [deg], Roll [deg] and Slip [nog te bepalen]
        self.compass.update(heading, headingBug)       # Heading [deg], HeadingBug [deg]

class PfdApp(App):
    def build(self):
        """
        Runs once, sets up the lay-out
        """
        Builder.load_file('horizon.kv')         # Load external .kv files
        Builder.load_file('compass.kv')
        Builder.load_file('bugbutton.kv')
        #________________
        self.serialDebug = True     # Print the serial datastream in console
        #¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
        self.pitch = 0          # Setup variables for the instance
        self.roll = 0
        self.slip = 0
        self.heading = 0
        self.headingBug = 0

        self.pfd = PFD()
        self.openPort()
        Clock.schedule_interval(self.updateDisplayElements, 1.0 / 50.0)
        return self.pfd


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

    def updateDisplayElements(self, dt):
        self.serialReadValues()
        self.pfd.update(self.pitch, self.roll, self.slip, self.heading, self.headingBug)

    def serialReadValues(self):
        try:
            
            serRead = self.ser.readline().decode('utf-8')       # Read line, make string ('utf-8')
            list_Str = serRead.split(';')                       # Put values in list

            if len(list_Str) == 5:
                self.pitch = list_Str[0]                            # Update class instance values
                self.roll = list_Str[1]
                self.slip = list_Str[2]
                self.heading = list_Str[3]
                self.headingBug = list_Str[4]
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
    
    # ________________________________________________________________________________________________
    # Seriële datafuncties

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

def main():
    PfdApp().run()


if __name__ == '__main__':
    main()