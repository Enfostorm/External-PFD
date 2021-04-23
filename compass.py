from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty

class Compass(Widget):
    pass

class HeadingBug(Widget):
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




class CompassApp(App):
    def build(self):
        compass = CompassEverything()
        return compass
        


def main():
    CompassApp().run()


if __name__ == '__main__':
    main()