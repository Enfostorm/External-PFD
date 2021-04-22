"""
25/3/2021   Peter van den Thillart

This code will make a virtual horizon based on the pitch and roll values provided.
It also takes care of the roll-indicator.

Inputs:     pitch, roll
Result:     Two-coloured rectangle which moves in accordance with the values.

I wanted to use AnchorLayout, but I couldn't get it to work. Floatlayout did work for me so I used that one.

Build-up of the layout:
  -  Stationary part
        - Roll triangle
        - Slip indicator (horizontal translation)
  -  Rotating part
        - stationary part
            - Rollindicator
        - vertically translating part
            - Horizon
            - Pitch gradations

All measurements are referenced to the height of the Everything-widget for it to automatically 
scale across different resolution screens.
"""


from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.config import Config


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

    def setRoll(self, roll):
        self.roll = roll

    def setPitch(self, pitch):
        self.ids.horPitchRoll.ids.horizpitch.ids.horizon.pitch = pitch
        self.ids.horPitchRoll.ids.horizpitch.ids.gradation.pitch = pitch
        self.ids.horPitchRoll.ids.horizpitch.ids.mask.pitch = pitch
    
    def setSlip(self, slip):
        self.ids.slipindicator.slip = slip

# =====================================================================================
class HorizonApp(App):
    def build(self):
        self.scale = 12
        self.bigLineWidth = 5
        self.medLineWidth = 2
        self.smallLineWidth = 1
        # Config.set('graphics', 'fullscreen', 'auto')

        displayedWidget = HorizonEverything()
        return displayedWidget

if __name__ == '__main__':
    HorizonApp().run()