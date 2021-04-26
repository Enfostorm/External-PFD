from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock

import serial
import serial.tools.list_ports

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
        r = Everything()        # r for remote
        self.pitchSlider = ValueSlider(min_val = -90, max_val = 90, role = 'Pitch')
        self.rollSlider = ValueSlider(min_val = -180, max_val = 180, role = 'Roll')
        self.slipSlider = ValueSlider(min_val = -0.01, max_val = 0.01, role = 'Slip')
        self.headingSlider = ValueSlider(min_val = -180, max_val = 180, role = 'Heading')
        self.headingBugSlider = ValueSlider(min_val = -180, max_val = 180, role = 'Heading bug')

        r.add_widget(self.pitchSlider)
        r.add_widget(self.rollSlider)
        r.add_widget(self.slipSlider)
        r.add_widget(self.headingSlider)
        r.add_widget(self.headingBugSlider)

        self.openPort()
        Clock.schedule_interval(self.serialWriteValues, 1/30)
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
        headingBug = self.headingBugSlider.ids.slider.value

        valueList = [pitch, roll, slip, heading, headingBug]
        
        self.ser.write(self.strForSerialOut(valueList).encode())

    
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