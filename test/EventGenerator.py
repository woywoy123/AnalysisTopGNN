from AnalysisTopGNN.Generators import EventGenerator 
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.IO import PickleObject, UnpickleObject
from AnalysisTopGNN.Samples import SampleTracer

def TestEventGenerator(Files):
    EvtGen = EventGenerator(Files)
    EvtGen.EventStop = 5
    EvtGen.EventStart = 1
    EvtGen.Event = Event
    EvtGen.SpawnEvents()
   
    it = 0
    for event in EvtGen:
        if event == EvtGen[event.Filename] == False:
            return False
        if event == EvtGen[it] == False:
            return False
        it += 1
    return True
