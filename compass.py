from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty

"""
Inputs:     Heading
            HeadingBug
            HeadingRate

Displayed elements:     Compass
                        Box with heading in degrees
                        Rate of Turn-indicator with increments at 3 and 6 deg/s.
"""
class Compass(Widget):
    pass

class HeadingBug(Widget):
    pass

class Airplane(Widget):
    pass

class HeadingRate(Widget):
    headingRate = NumericProperty(12)

    degPerIncrement = 15

    def setHeadingRate(self, headingRate):
        self.headingRate = self.headingRateUnitScaling(headingRate)

    def headingRateUnitScaling(self, headingRateDegPerS):
        # Transform degrees/s to degrees of deflection of the indicator
        # 1 division is a standard rate of turn of 3°/s (2-minute turn)
        degPerDiv = self.degPerIncrement
        return headingRateDegPerS/3*degPerDiv

class HeadingDisplay(Widget):
    pos_hint_x = NumericProperty(0.5)
    pos_hint_y = NumericProperty(0.9)
    scale = NumericProperty(1)

    headingLabel = ObjectProperty()

# Points for ________
#           |___  ___|
#               \/
    p1x = 0
    p1y = 0
    
    p2x = -15
    p2y = 15
    
    p3x = -40
    p3y = 15
    
    p4x = p3x
    p4y = 50
    
    p5x = -p4x
    p5y = p4y
    
    p6x = -p3x
    p6y = p3y
    
    p7x = -p2x
    p7y = p3y
    
    p8x = p1x
    p8y = p1y

    def setHeading(self, heading):
        self.headingLabel.text = f'{heading}°'

class GroundTrack(Widget):
    pass
    




# ========================================================================================================
class CompassEverything(Widget):           # Full layout
    heading = NumericProperty(0)
    headingBug = NumericProperty(0)
    turnRate = NumericProperty()
    groundTrack = NumericProperty(5)

    headingDisp = ObjectProperty()
    headingRate = ObjectProperty()


    def update(self, heading, headingBug, headingRate, groundTrack):
        self.setHeading(heading)
        self.setHeadingBug(headingBug)
        self.setHeadingRate(headingRate)
        self.setGroundTrack(groundTrack)

    def setHeading(self, heading):
        self.heading = heading
        self.headingDisp.setHeading(heading)
    def setHeadingBug(self, headingBug):
        self.headingBug = headingBug
    def setHeadingRate(self, headingRate):
        self.headingRate.setHeadingRate(headingRate)
    def setGroundTrack(self, groundTrack):
        self.groundTrack = groundTrack

# =========================================================================================================
class CompassApp(App):
    def build(self):
        self.compass = CompassEverything()
        self.compass.update(46, 20, 3, -3)
        return self.compass
        # return HeadingRate()


def main():
    CompassApp().run()


if __name__ == '__main__':
    main()