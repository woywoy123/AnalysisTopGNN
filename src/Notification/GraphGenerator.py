from .Notification import Notification
from AnalysisG.Tracer import SampleTracer


class _GraphGenerator(Notification):
    def __init__(self, inpt):
        if inpt == None:
            return
        if issubclass(type(inpt), SampleTracer):
            self += inpt
        else:
            self.WrongInput()

    def WrongInput(self):
        self.Warning("Input instance is of wrong type. Skipping...")

    def CheckGraphImplementation(self):
        if self.EventGraph != None:
            return True
        ex = "Or do: from AnalysisTopGNN.Events import Event"
        self.Failure("=" * len(ex))
        self.Failure("No Graph Implementation Provided.")
        self.Failure("var = " + self.Caller.capitalize() + "()")
        self.Failure("var.EventGraph")
        self.Failure("See src/Events/Graphs/EventGraphs.py or 'tutorial'")
        self.Failure("=" * len(ex))
        return False

    def CheckSettings(self):
        if self._condor:
            return True
        attrs = 3
        attrs -= (
            1 * self.Warning("NO EDGE FEATURES PROVIDED")
            if len(list(self.EdgeAttribute)) == 0
            else 0
        )
        attrs -= (
            1 * self.Warning("NO NODE FEATURES PROVIDED")
            if len(list(self.NodeAttribute)) == 0
            else 0
        )
        attrs -= (
            1 * self.Warning("NO GRAPH FEATURES PROVIDED")
            if len(list(self.GraphAttribute)) == 0
            else 0
        )
        if attrs != 0:
            return self.Success("Data being processed on: " + self.Device)

        message = "NO ATTRIBUTES DEFINED!"
        self.Failure("=" * len(message))
        self.Failure(message)
        return self.Failure("=" * len(message))
