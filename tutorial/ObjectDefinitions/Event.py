from AnalysisG.Templates import EventTemplate
from ObjectDefinitions.Particles import Jet

class ExampleEvent(EventTemplate):

    def __init__(self):
        EventTemplate.__init__(self)
        self.Objects = {
            "Jet" : Jet()
        }

        self.Trees = ["nominal"]
        self.weight = "weight_mc"

    def CompileEvent(self):
        self.Out = []

        # If we have more than one tree in the sample, we can override
        # which one to run by using a routing condition
        if self.Tree == "<Something>": return

        # We only have this one in the example samples
        if self.Tree == "nominal": pass
        else: return

        # Run this on nominal
        for i in self.Jet:
            # Do some matching or just simply change the variable name
            self.Out.append(self.Jet[i])

        # create a new event attribute
        self.nJets = len(self.Out)
        self.signal = 1 # add some truth attribute for the graph tutorial
