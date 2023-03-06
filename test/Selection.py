from ExampleSelection import Example, Example2
from AnalysisTopGNN import Analysis
from AnalysisTopGNN.Events import Event

def TestSelection(Files):
    AnaE = Analysis()
    AnaE.ProjectName = "Project"
    AnaE.InputSample("bsm-4t", "/".join(Files[0].split("/")[:-1]))
    AnaE.InputSample("t", Files[1])
    AnaE.AddSelection("Example", Example)
    AnaE.AddSelection("Example2", Example2())
    AnaE.MergeSelection("Example")
    AnaE.MergeSelection("Example2")
    AnaE.Event = Event
    AnaE.EventCache = True
    AnaE.DumpPickle = True
    AnaE.Threads = 12
    AnaE.VerboseLevel = 1
    AnaE.Launch()
    
    it = 0
    c = 0
    y = []
    for i in AnaE:
        c += len(i.Trees["nominal"].TopChildren)
        t = Example2()
        t._EventPreprocessing(i)
        y.append(t)
        if it == 10:
            break
        it += 1
    l = len(y) 
    x = sum(y)
    if l != len(x._TimeStats):
        return False
    if l != x._CutFlow["Success->Example"]:
        return False
    if l*4 != len(x.Top["Truth"]):
        return False
    if len(x.Children["Truth"]) != c:
        return False
    
    if l != len(x._TimeStats):
        return False
    if l != x._CutFlow["Success->Example"]:
        return False
    if l*4 != len(x.Top["Truth"]):
        return False
    if len(x.Children["Truth"]) != c:
        return False
    return True
