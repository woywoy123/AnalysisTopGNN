from AnalysisG._cmodules.SampleTracer import SampleTracer
from .Notification import Notification

class _SelectionGenerator(Notification):
    def __init__(self, inpt):
        if inpt == None: return
        if issubclass(type(inpt), SampleTracer): self += inpt
        else: self.WrongInput()

    def WrongInput(self):
        self.Warning("Input instance is of wrong type. Skipping...")

    def CheckSettings(self, sample = None):
        if sample is not None: pass
        else: sample = self
        msg = "Selections not specified..."
        if not len(self.Selections): return self.Warning(msg)
        msg = "No compiled events were found..."
        if not len(sample): return self.Failure(msg)
