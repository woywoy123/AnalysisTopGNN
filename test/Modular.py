from AnalysisTopGNN.Generators import EventGenerator
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.IO import PickleObject, UnpickleObject
from AnalysisTopGNN.Generators import Analysis

def TestEventGenerator(Files):
   
    File0 = {"/".join(Files[0].split("/")[:-1]) : [Files[0].split("/")[-1]]}
    File1 = {"/".join(Files[1].split("/")[:-1]) : [Files[1].split("/")[-1]]}   
   
    End = 12

    ev0 = EventGenerator(File0)
    ev0.Event = Event
    ev0.EventStart = 0
    ev0.EventStop = End
    ev0.SpawnEvents()
    
    ev1 = EventGenerator(File1)
    ev1.Event = Event
    ev1.EventStart = 0
    ev1.EventStop = End
    ev1.SpawnEvents()
   
    combined = ev0 + ev1
    Object0 = {}
    for i in ev0:
        Object0[i.Filename] = i
    
    Object1 = {}
    for i in ev0:
        Object1[i.Filename] = i
    
    ObjectSum = {}
    for i in combined:
        ObjectSum[i.Filename] = i
    
    for i in Object0:
        if ObjectSum[i] == Object0[i]:
            continue
        print("Error: i", i, " obj", ObjectSum[i])

    for i in Object1:
        if ObjectSum[i] == Object0[i]:
            continue
        print("Error: i", i, " obj", ObjectSum[i])

    combined = combined + ev0 + ev1
    ObjectSum = {}
    for i in combined:
        ObjectSum[i.Filename] = i
    
    for i in Object0:
        if ObjectSum[i] == Object0[i]:
            continue
        print("Error: i", i, " obj", ObjectSum[i])

    for i in Object1:
        if ObjectSum[i] == Object0[i]:
            continue
        print("Error: i", i, " obj", ObjectSum[i])
    
    print(len(ObjectSum), len(Object0), len(Object1))


    def EventGen(Dir, Name):
        Ana = Analysis()
        Ana.ProjectName = "TMPProject"
        Ana.InputSample(Name, Dir)
        Ana.EventCache = True
        Ana.Event = Event
        Ana.Threads = 4
        Ana.chnk = 4
        Ana.EventStart = 0
        Ana.EventStop = End
        Ana.DumpHDF5 = True
        Ana.DumpPickle = True
        Ana.Launch()
        return Ana

    ev = EventGen(File0, "Tops")
    ev += EventGen(File1, "Top")
    
    passing = False
    for i in ev:
        passing = ev[i.Filename].Filename == i.Filename
        if passing == False:
            return False
    return passing

def TestAnalysis(Files):
    AnaE = Analysis()
    AnaE.ProjectName = "Project"
    AnaE.InputSample("bsm-4t", "/".join(Files[0].split("/")[:-1]))
    AnaE.InputSample("t", Files[1])
    AnaE.Event = Event
    AnaE.EventCache = True
    AnaE.Threads = 12
    AnaE.EventStop = 100
    AnaE.DumpPickle = True
    AnaE.Launch()
    
    it = 0
    for i in AnaE:
        it += 1
    if it == 0:
        return False
    return True

def TestLargeSample(File):
    AnaE = Analysis()
    AnaE.ProjectName = "Project"
    AnaE.InputSample("l", File)
    AnaE.Threads = 12
    AnaE.Event = Event
    AnaE.EventCache = True
    AnaE.Launch()

    return True
