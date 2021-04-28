from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.behaviors.button import ButtonBehavior

class NumberDisplay(Widget):
    numberLabel = ObjectProperty()

class SpeedButton(Widget):
    functionLabel = ObjectProperty()
    numberDisplay = ObjectProperty()

    def setFunctionLabel(self, newLabel):
        self.functionLabel.text = newLabel

    def setValue(self, value, unit):        # Past de onderste tekstwaarde aan met een spatie tussen de twee.
        self.numberDisplay.numberLabel.text = f'{value:.0f} {unit}' # Waarden weergeven met een f string (zet er hier een spatie tussen)

class AltitudeButton(Widget):
    functionLabel = ObjectProperty()
    numberDisplay = ObjectProperty()

    def setFunctionLabel(self, newLabel):
        self.functionLabel.text = newLabel

    def setValue(self, value, unit):        # Past de onderste tekstwaarde aan met een spatie tussen de twee.
        self.numberDisplay.numberLabel.text = f'{value:.0f} {unit}' # Waarden weergeven met een f string (zet er hier een spatie tussen)

class VSIButton(Widget):
    functionLabel = ObjectProperty()
    numberDisplay = ObjectProperty()

    def setFunctionLabel(self, newLabel):
        self.functionLabel.text = newLabel

    def setValue(self, value, unit):        # Past de onderste tekstwaarde aan met een spatie tussen de twee.
        self.numberDisplay.numberLabel.text = f'{value:.0f} {unit}' # Waarden weergeven met een f string (zet er hier een spatie tussen)

class HeadingButton(Widget):
    functionLabel = ObjectProperty()
    numberDisplay = ObjectProperty()

    def setFunctionLabel(self, newLabel):
        self.functionLabel.text = newLabel

    def setValue(self, value, unit):        # Past de onderste tekstwaarde aan met een spatie tussen de twee.
        self.numberDisplay.numberLabel.text = f'{value:.0f} {unit}' # Waarden weergeven met een f string (zet er hier een spatie tussen)


class BugSelectors(Widget):
    headingButton = ObjectProperty()
    speedButton = ObjectProperty()
    altButton = ObjectProperty()
    vsiButton = ObjectProperty()

    def __init__(self, **kwargs):
        super(BugSelectors, self).__init__(**kwargs)
        self.hdgORspd = 'hdg'
        self.altORvsi = 'alt'

    def headingActive(self):
        self.hdgORspd = 'hdg'
    def speedActive(self):
        self.hdgORspd = 'spd'
    def altActive(self):
        self.altORvsi = 'alt'
    def vsiActive(self):
        self.altORvsi = 'vsi'

    def setHeadingFunction(self, func):
        self.headingButton.setFunctionLabel(func)
    def setSpeedFunction(self, func):
        self.speedButton.setFunctionLabel(func)
    def setAltFunction(self, func):
        self.altButton.setFunctionLabel(func)
    def setVsiFunction(self, func):
        self.vsiButton.setFunctionLabel(func)

    def setHeadingValue(self, val, unit):
        self.headingButton.setValue(val, unit)
    def setSpeedValue(self, val, unit):
        self.speedButton.setValue(val, unit)
    def setAltValue(self, val, unit):
        self.altButton.setValue(val, unit)
    def setVsiValue(self, val, unit):
        self.vsiButton.setValue(val, unit)

    def printInfo(self):
        print(f'{self.hdgORspd} {self.altORvsi}')




class BugSettingsApp(App):
    def build(self):
        l = BugSelectors()
        l.hdgORspd = 'hdg'
        l.altORvsi = 'alt'
        return l





def main():
    BugSettingsApp().run()


if __name__ == '__main__':
    main()