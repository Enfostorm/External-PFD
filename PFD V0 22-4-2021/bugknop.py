from kivy.app import App
from kivy.uix.widget import Widget
from kivy.config import Config

from kivy.clock import Clock
import math

class BugButton(Widget):
    def __init__(self, **kwargs):
        super(BugButton, self).__init__(**kwargs)
        self.counter = 0.0
        self.firstrun = True

    def setFunctionLabel(self, newLabel):
        self.ids.functionLabel.text = newLabel

    def setValue(self, value, unit):        # Past de onderste tekstwaarde aan met een spatie tussen de twee.
        self.ids.numberDisplay.ids.numberLabel.text = f'{value:.0f} {unit}' # Waarden weergeven met een f string (zet er hier een spatie tussen)

    def updateValues(self, dt):
        if self.firstrun:
            self.numberRange = 20000         # Bepaalt het bereik van de waarden 
            self.lowestNumber = 15000
            self.firstrun = False

        self.counter += 0.005
        self.normalisedValue = (math.cos(self.counter) + 1) / 2                    # Genereert sinuswaarden van 0 tot 1
        self.value = round((self.lowestNumber + self.numberRange * self.normalisedValue) / 100) * 100
        self.setValue(self.value, 'ft')



class NumberDisplay(Widget):
    pass

class KnopDemoApp(App):
    def build(self):
        Config.set('graphics', 'width', '180')      # resolutie van het scherm
        Config.set('graphics', 'height', '100')

        button = BugButton()                        # Aanmaken van de knop
        button.setValue(35000, 'ft')                # Labels van de knop instellen
        button.setFunctionLabel('ALT bug')
        
        Clock.schedule_interval(button.updateValues, 1/60)
        return button

if __name__ == '__main__':
    KnopDemoApp().run()