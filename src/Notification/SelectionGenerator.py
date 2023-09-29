from .Notification import Notification
from AnalysisG.Tracer import SampleTracer


class _SelectionGenerator(Notification):
    def __init__(self, inpt):
        if inpt == None:
            return
        if issubclass(type(inpt), SampleTracer):
            self += inpt
        else:
            self.WrongInput()

    def WrongInput(self):
        self.Warning("Input instance is of wrong type. Skipping...")

    def CheckSettings(self):
        if len(self.Selections) == 0 and len(self.Merge) == 0:
            return self.Warning("No Selection was specified...")
        if len(self) == 0:
            return self.Failure("No compiled events were found...")
