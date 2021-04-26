from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import ButtonBehavior
from kivy.properties import ObjectProperty


class BugButton(ButtonBehavior, Widget):
    functionLabel = ObjectProperty()
    numberDisplay = ObjectProperty()
    button = ObjectProperty()

    def __init__(self, **kwargs):
        super(BugButton, self).__init__(**kwargs)
        self.counter = 0.0
        self.firstrun = True

    def setFunctionLabel(self, newLabel):
        self.functionLabel.text = newLabel

    def setValue(self, value, unit):        # Past de onderste tekstwaarde aan met een spatie tussen de twee.
        self.numberDisplay.numberLabel.text = f'{value:.0f} {unit}' # Waarden weergeven met een f string (zet er hier een spatie tussen)

    def returnButton(self):
        return self.button

class NumberDisplay(Widget):
    numberLabel = ObjectProperty()

# ========================================================================================
class BugButtonApp(App):
    def build(self):
        bb = BugButton()
        bb.setFunctionLabel('VSI')
        bb.setValue(35000, 'ft')
        return bb
        


def main():
    BugButtonApp().run()


if __name__ == '__main__':
    main()