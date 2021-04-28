from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock

import serial
import serial.tools.list_ports

import threading
import time

class ValueSlider(Widget):
    min_val = NumericProperty(0)
    max_val = NumericProperty(0)
    label = StringProperty(None)
    role = StringProperty(None)
    def __init__(self, **kwargs):
        super(ValueSlider, self).__init__(**kwargs)
        self.min_val = kwargs['min_val']
        self.max_val = kwargs['max_val']
        self.label = 'unassigned'
        self.role = 'unassigned'

class SliderStack(BoxLayout):
    pass

class SerialRemoteApp(App):
    def __init__(self, **kwargs):
        super(SerialRemoteApp, self).__init__(**kwargs)

    def build(self):
        r = SliderStack()        # r for remote
        self.bugLayout = GridLayout(cols = 2, size_hint_x = 2)
        self.pitchSlider = ValueSlider(min_val = -90, max_val = 90, role = 'Pitch')
        self.rollSlider = ValueSlider(min_val = -180, max_val = 180, role = 'Roll')
        self.slipSlider = ValueSlider(min_val = -0.01, max_val = 0.01, role = 'Slip')
        self.headingSlider = ValueSlider(min_val = -180, max_val = 180, role = 'Heading')
        self.altitudeSlider = ValueSlider(min_val = 0, max_val = 50000, role = 'Altitude')
        self.speedSlider = ValueSlider(min_val = 0, max_val = 500, role = 'Speed')

        self.headingRateSlider = ValueSlider(min_val = -20, max_val = 20, role = 'Heading Rate')
        self.vSpeedSlider = ValueSlider(min_val = -20, max_val = 20, role = 'Vertical Speed')
        self.deltaSpeedSlider = ValueSlider(min_val = -20, max_val = 20, role = 'Acceleration Rate')

        self.headingBugSlider = ValueSlider(min_val = 0, max_val = 360, role = 'Heading Bug')
        self.altBugSlider = ValueSlider(min_val = 0, max_val = 50000, role = 'Altitude Bug')
        self.spdBugSlider = ValueSlider(min_val = 0, max_val = 500, role = 'Speed bug')
        self.vsiBugSlider = ValueSlider(min_val = -20, max_val = 20, role = 'VSI Bug')

        self.groundTrackSlider = ValueSlider(min_val = -30, max_val = 30, role = 'Ground Track')



        self.bugLayout.add_widget(self.headingBugSlider)
        self.bugLayout.add_widget(self.altBugSlider)
        self.bugLayout.add_widget(self.spdBugSlider)
        self.bugLayout.add_widget(self.vsiBugSlider)

        r.add_widget(self.pitchSlider)
        r.add_widget(self.rollSlider)
        r.add_widget(self.slipSlider)
        r.add_widget(self.headingSlider)
        r.add_widget(self.altitudeSlider)
        r.add_widget(self.speedSlider)
        r.add_widget(self.bugLayout)
        r.add_widget(self.groundTrackSlider)

        self.openPort()
        Clock.schedule_interval(self.serialWriteValues, 1/60)
        threading.Thread(target=self.serialReadValuesThread, daemon=True).start()       # Daemon = True so thread closes when the main process closes
        return r

    def openPort(self):
        self.ser = serial.Serial(port=self.autoSelectPort(),
                                    baudrate=115200,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    bytesize=serial.EIGHTBITS,
                                    timeout=1)
    
    def serialWriteValues(self, dt):
        pitch = self.pitchSlider.ids.slider.value
        roll = self.rollSlider.ids.slider.value
        slip = self.slipSlider.ids.slider.value
        heading = self.headingSlider.ids.slider.value
        altitude = self.altitudeSlider.ids.slider.value
        speed = self.speedSlider.ids.slider.value

        headingRate = self.headingRateSlider.ids.slider.value
        vSpeed = self.vSpeedSlider.ids.slider.value
        deltaSpeed = self.deltaSpeedSlider.ids.slider.value

        headingBug = self.headingBugSlider.ids.slider.value
        altBug = self.altBugSlider.ids.slider.value
        spdBug = self.spdBugSlider.ids.slider.value
        vsiBug = self.vsiBugSlider.ids.slider.value

        groundTrack = self.groundTrackSlider.ids.slider.value

        valueList = [pitch, roll, slip, heading, altitude, speed, headingRate, vSpeed, deltaSpeed, headingBug, altBug, spdBug, vsiBug, groundTrack]
        
        self.ser.write(self.strForSerialOut(valueList).encode())

    def serialReadValuesThread(self):
        # Continuously reads serial data, but has to be run in a separate thread, otherwise the program will hang until a line has been received.
        expected_length = 4
        while True:
            try:
                serRead = self.ser.readline().decode('utf-8')
                list_Str = serRead.split(';')

                if len(list_Str) == expected_length:
                    self.headingBug = self.headingBugSlider.ids.slider.value = float(list_Str[0])
                    self.altBug = self.altBugSlider.ids.slider.value = float(list_Str[1])
                    self.spdBug = self.spdBugSlider.ids.slider.value = float(list_Str[2])
                    self.vsiBug = self.vsiBugSlider.ids.slider.value = float(list_Str[3])
            except:
                print('No serial data could be read, sleeping for 1s')
                time.sleep(1)

    
    def autoSelectPort(self):
    # Zoekt tussen de seriele poorten naar een poort die in de beschrijving het keyword heeft staan.
        keyword = 'UART'

        for p in serial.tools.list_ports.comports():
            # print(p)
            if keyword in p.description:
                print(f'Found port {p.device}')
                return p.device

        try:
            print(f'No ports automatically found, falling back to /dev/ttyS0')   # Prints if no keyword has been found
            return '/dev/ttyS0'
        except:
            print('No usable ports found, no port opened')

    def roundedStr(self, number, afterComma):
        # returns a string rounded to afterComma places after the comma
        return str(round(pow(10, afterComma)*number)/pow(10, afterComma))

    def strForSerialOut(self, valueList):
        strVariables = [self.roundedStr(element, 4) for element in valueList]
        dataString = ';'.join(strVariables)
        stringToWrite = dataString + '\n'
        return stringToWrite


def main():
    SerialRemoteApp().run()


if __name__ == '__main__':
    main()