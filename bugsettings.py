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
    button = ObjectProperty()

    def setFunctionLabel(self, newLabel):
        self.functionLabel.text = newLabel

    def setValue(self, value, unit):        # Past de onderste tekstwaarde aan met een spatie tussen de twee.
        self.numberDisplay.numberLabel.text = f'{value:.0f} {unit}' # Waarden weergeven met een f string (zet er hier een spatie tussen)

    def setState(self, state):
        self.button.state = state


class AltitudeButton(Widget):
    functionLabel = ObjectProperty()
    numberDisplay = ObjectProperty()
    button = ObjectProperty()

    def setFunctionLabel(self, newLabel):
        self.functionLabel.text = newLabel

    def setValue(self, value, unit):        # Past de onderste tekstwaarde aan met een spatie tussen de twee.
        self.numberDisplay.numberLabel.text = f'{value:.0f} {unit}' # Waarden weergeven met een f string (zet er hier een spatie tussen)

    def setState(self, state):
        self.button.state = state


class VSIButton(Widget):
    functionLabel = ObjectProperty()
    numberDisplay = ObjectProperty()
    button = ObjectProperty()

    def setFunctionLabel(self, newLabel):
        self.functionLabel.text = newLabel

    def setValue(self, value, unit):        # Past de onderste tekstwaarde aan met een spatie tussen de twee.
        self.numberDisplay.numberLabel.text = f'{value:.0f} {unit}' # Waarden weergeven met een f string (zet er hier een spatie tussen)

    def setState(self, state):
        self.button.state = state


class HeadingButton(Widget):
    functionLabel = ObjectProperty()
    numberDisplay = ObjectProperty()
    button = ObjectProperty()

    def setFunctionLabel(self, newLabel):
        self.functionLabel.text = newLabel

    def setValue(self, value, unit):        # Past de onderste tekstwaarde aan met een spatie tussen de twee.
        self.numberDisplay.numberLabel.text = f'{value:.0f} {unit}' # Waarden weergeven met een f string (zet er hier een spatie tussen)

    def setState(self, state):
        self.button.state = state


class BugSelectors(Widget):
    headingButton = ObjectProperty()
    speedButton = ObjectProperty()
    altButton = ObjectProperty()
    vsiButton = ObjectProperty()

    def __init__(self, **kwargs):
        super(BugSelectors, self).__init__(**kwargs)
        self.hdgORspd = 'hdg'
        self.altORvsi = 'alt'
        # self.headingButton.setState('down')
        # self.altButton.setState('down')

    def updateValues(self, headingValue, speedValue, altValue, vsiValue, speedUnit, altUnit, vsiUnit):
        self.setHeadingValue(headingValue)
        self.setSpeedValue(speedValue, speedUnit)
        self.setAltValue(altValue, altUnit)
        self.setVsiValue(vsiValue, vsiUnit)

    def headingActive(self):
        self.hdgORspd = 'hdg'
        self.speedButton.setState('normal')
        self.headingButton.setState('down')
    def speedActive(self):
        self.hdgORspd = 'spd'
        self.speedButton.setState('down')
        self.headingButton.setState('normal')
    def altActive(self):
        self.altORvsi = 'alt'
        self.altButton.setState('down')
        self.vsiButton.setState('normal')
    def vsiActive(self):
        self.altORvsi = 'vsi'
        self.altButton.setState('normal')
        self.vsiButton.setState('down')

    def setHeadingFunction(self, func):
        self.headingButton.setFunctionLabel(func)
    def setSpeedFunction(self, func):
        self.speedButton.setFunctionLabel(func)
    def setAltFunction(self, func):
        self.altButton.setFunctionLabel(func)
    def setVsiFunction(self, func):
        self.vsiButton.setFunctionLabel(func)

    def setHeadingValue(self, val):
        self.headingButton.setValue(val, '°')
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