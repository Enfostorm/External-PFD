"""
Jonas Beernaert

This code will show a compass displaying a heading, plane icon and a heading bug

code:
    - compass
    - heading Bug
    - Airplane 
    - pointer

"""
import kivy
from kivy.app import App 
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock


class Compass(Widget):
    pass

class HeadingBug(Widget):
    pass

class Airplane(Widget):
    pass

class Pointer(Widget):
    pass


class CompassEverything(Widget):           # Full layout
    heading = NumericProperty(8)
    headingBug = NumericProperty(-42)
    turnRate = NumericProperty()


    def setHeading(self, heading):
        self.heading = heading

    def setHeadingBug(self, headingBug):
        self.headingBug = headingBug

    


class CompassApp(App):
    def build(self):
        displayedWidget = CompassEverything()
        CompassEverything.heading
        CompassEverything.headingBug
        return displayedWidget


if __name__ == "__main__":
    CompassApp().run()



