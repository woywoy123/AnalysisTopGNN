from AnalysisG.Templates import EventTemplate
from ObjectDefinitions.Particles import Jet

class ExampleEvent(EventTemplate):

    def __init__(self):
        EventTemplate.__init__(self)
        self.Objects = {
            "Jet" : Jet()
        }
    
        self.Trees = ["nominal_Loose;7"] 
        self.weight = "weight_mc"

    def CompileEvent(self):
        self.Out = []
       
        # Apply the below only on this tree
        if self.Tree == "<Something>": return 
        if self.Tree == "nominal_Loose;7": pass
        else: return 

        for i in self.Jet:
            # Do something 
            self.Out.append(self.Jet[i])
        



