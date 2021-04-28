from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class Horizon(Widget):      # Blue and brown rectangles as background
    pitch = NumericProperty(0)
    scale = 12

    def setPitch(self, pitch):
        self.pitch = pitch

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

class HorizonPitchAndRoll(Widget):
    horizon = ObjectProperty()
    gradation = ObjectProperty()
    mask = ObjectProperty()

    def setPitch(self, pitch):
        self.horizon.setPitch(pitch)
        self.gradation.pitch = pitch
        self.mask.pitch = pitch

class RollTriangle(Widget):         # Triangle to indicate on rollindicatorring
    pass

class SlipIndicator(Widget):        # Rectangle under the RollTriangle which indicates sideways slip
    slip = NumericProperty(0)


# =====================================================================================
class HorizonEverything(Widget):           # Full layout
    roll = NumericProperty(0)

    horPitchRoll = ObjectProperty()
    slipindicator = ObjectProperty()

    def update(self, pitch, roll, slip):
        self.updatePitch(pitch)
        self.updateRoll(roll)
        self.updateSlip(slip)

    def updateRoll(self, roll):
        self.roll = roll

    def updatePitch(self, pitch):
        self.horPitchRoll.setPitch(pitch)
    
    def updateSlip(self, slip):
        self.slipindicator.slip = slip

# =====================================================================================
class HorizonApp(App):
    def build(self):
        self.scale = 12
        # Config.set('graphics', 'fullscreen', 'auto')

        displayedWidget = HorizonEverything()
        return displayedWidget

if __name__ == '__main__':
    HorizonApp().run()