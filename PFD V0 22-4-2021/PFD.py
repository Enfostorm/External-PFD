from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock

# Imports voor seriële data
import serial
import serial.tools.list_ports

# ==================================================================================================
# ===================================== Sectie PFD =================================================
# ==================================================================================================
class PFD(Widget):
    def update(self, pitch, roll, slip, heading, headingBug):
        self.ids.horizon.update(pitch, roll, slip)       # Pitch [deg], Roll [deg] and Slip [nog te bepalen]
        self.ids.compass.update(heading, headingBug)       # Heading [deg], HeadingBug [deg]



# ==================================================================================================
# ===================================== Sectie Horizon =============================================
# ==================================================================================================
class Horizon(Widget):      # Blue and brown rectangles as background
    pitch = NumericProperty(0)
    scale = 12

class HorizonMask(FloatLayout):
    pitch = Horizon.pitch
    scale = Horizon.scale
    tightness = 0.13     # Width of the transparent band in the center. Smaller = wider gap

class PitchGradationSegment(Widget):
    scale = Horizon.scale       # amount of 10-deg increments that would fit in the full vertical space
    bigLineWidth = 5    # Relative sizes of the lines
    medLineWidth = 2
    smallLineWidth = 1

class PitchGradationFull(Widget):
    scale = PitchGradationSegment.scale
    bigLineWidth = PitchGradationSegment.bigLineWidth
    pitch = Horizon.pitch

class HorizonAndPitch(FloatLayout):       # Horizon + rollindicatorring
    scale = PitchGradationSegment.scale
    pitch = Horizon.pitch

class HorizonPitchAndRoll(Widget):
    pass

class RollTriangle(Widget):         # Triangle to indicate on rollindicatorring
    pass

class SlipIndicator(Widget):        # Rectangle under the RollTriangle which indicates sideways slip
    slip = NumericProperty(0.008)


# =====================================================================================
class HorizonEverything(Widget):           # Full layout
    roll = NumericProperty(0)

    def update(self, pitch, roll, slip):
        self.setPitch(pitch)
        self.setRoll(roll)
        self.setSlip(slip)

    def setRoll(self, roll):
        self.roll = roll

    def setPitch(self, pitch):
        self.ids.horPitchRoll.ids.horizpitch.ids.horizon.pitch = pitch
        self.ids.horPitchRoll.ids.horizpitch.ids.gradation.pitch = pitch
        self.ids.horPitchRoll.ids.horizpitch.ids.mask.pitch = pitch
    
    def setSlip(self, slip):
        self.ids.slipindicator.slip = slip
# ==================================================================================================
# ===================================== Sectie Kompas ==============================================
# ==================================================================================================
class Compass(Widget):
    pass

class HeadingBug(Widget):       # TODO bug draait niet mee met het kompas!!!!!!!
    pass

class Airplane(Widget):
    pass

class Pointer(Widget):
    pass


class CompassEverything(Widget):           # Full layout
    heading = NumericProperty(0)
    headingBug = NumericProperty(0)
    turnRate = NumericProperty()

    def update(self, heading, headingBug):
        self.setHeading(heading)
        self.setHeadingBug(headingBug)

    def setHeading(self, heading):
        self.heading = heading

    def setHeadingBug(self, headingBug):
        self.headingBug = headingBug

# ==================================================================================================
# ===================================== Sectie Bugknop =============================================
# ==================================================================================================
class BugButton(Widget):
    def __init__(self, **kwargs):
        super(BugButton, self).__init__(**kwargs)
        self.counter = 0.0
        self.firstrun = True

    def setFunctionLabel(self, newLabel):
        self.ids.functionLabel.text = newLabel

    def setValue(self, value, unit):        # Past de onderste tekstwaarde aan met een spatie tussen de twee.
        self.ids.numberDisplay.ids.numberLabel.text = f'{value:.0f} {unit}' # Waarden weergeven met een f string (zet er hier een spatie tussen)

    # def updateValues(self, dt):
    #     if self.firstrun:
    #         self.numberRange = 20000         # Bepaalt het bereik van de waarden 
    #         self.lowestNumber = 15000
    #         self.firstrun = False

    #     self.counter += 0.005
    #     self.normalisedValue = (math.cos(self.counter) + 1) / 2                    # Genereert sinuswaarden van 0 tot 1
    #     self.value = round((self.lowestNumber + self.numberRange * self.normalisedValue) / 100) * 100
    #     self.setValue(self.value, 'ft')



class NumberDisplay(Widget):
    pass

# ==================================================================================================
# ===================================== Sectie PFDApp ==============================================
# ==================================================================================================
class PfdApp(App):
    def build(self):
        """
        Runs once, sets up the lay-out
        """
        #________________
        self.serialDebug = True
        #¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
        trigger = Clock.create_trigger(self.updateDisplayElements)
        self.pitch = 0
        self.roll = 0
        self.slip = 0
        self.heading = 0
        self.headingBug = 0

        self.pfd = PFD()
        self.openPort()
        Clock.schedule_interval(trigger, 1.0 / 50.0)
        return self.pfd

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

    def openPort(self):
        port = self.autoSelectPort()
        self.BAUD = 115200
        try:
            self.ser = serial.Serial(port = port,                      # Setup serial connection
                                baudrate = self.BAUD,
                                parity = serial.PARITY_NONE,
                                stopbits = serial.STOPBITS_ONE,
                                bytesize = serial.EIGHTBITS,
                                timeout = 1)
        except:
            print('failed to find suitable port')

def main():
    PfdApp().run()


if __name__ == '__main__':
    main()