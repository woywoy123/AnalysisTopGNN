from AnalysisTopGNN.Generators import EventGenerator, GraphGenerator
from AnalysisTopGNN.Events import Event, EventGraphChildren
from AnalysisTopGNN.IO import PickleObject, UnpickleObject
from AnalysisTopGNN.Tools import Tools

def Test(a):
    return 1

def TestEventGraph(Files):
   
    Ev = EventGenerator(Files)
    Ev.EventStart = 0
    Ev.EventStop = 100
    Ev.Event = Event
    Ev.SpawnEvents()

    Gr = GraphGenerator()
    Gr += Ev
    Gr.EventGraph = EventGraphChildren
    Gr.AddGraphFeature(Test)
    Gr.TestFeatures(10)
    Gr.EventStart = 1
    Gr.EventStop = 100
    Gr.CompileEventGraph()
    
    if len(Gr) != 100:
        return False
    for i in Gr:
        if i.Compiled == False:
            return False
        if Gr.HashToROOT(i.Filename) == None:
            return False
    return True 
