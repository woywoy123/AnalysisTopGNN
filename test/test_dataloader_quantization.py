from AnalysisG.Events import Event, GraphChildren
from AnalysisG.Templates import ApplyFeatures
from AnalysisG.Generators import Optimizer
from AnalysisG import Analysis

from examples.EventOther import EventOther
from examples.Event import EventEx

from torch_geometric.loader import DataListLoader
from conftest import clean_dir
import torch
import time

smpl = "samples/dilepton/"


def test_normal():
    ana = Analysis(smpl)
    ana.Event = Event
    ana.EventCache = True
    ana.Launch()
    lst = []
    for i in ana:
        assert i.Event
        lst.append(i)
    assert len(lst) != 0

    ana = Analysis(smpl)
    ana.DataCache = True
    ana.EventGraph = GraphChildren
    ApplyFeatures(ana, "TruthChildren")
    ana.Launch
    lst = []
    for i in ana:
        assert i.clone().i
        assert i.Graph
        lst.append(i)
    assert len(lst) != 0
    clean_dir()


def test_quant():
    ana = Analysis(smpl)
    ana.EventCache = True
    ana.Event = Event
    ana.Launch()

    ana = Analysis(smpl)
    ana.DataCache = True
    ana.EventGraph = GraphChildren
    ApplyFeatures(ana, "TruthChildren")
    ana.Launch()

    ana = Analysis()
    ana.TrainingSize = 50
    ana.kFolds = 10
    ana.Launch()

    ana = Optimizer(ana)
    ana.DataCache = True
    ana.Device = "cuda"
    ana._outDir = ana.OutputDirectory + "/Training"
    ana._searchdatasplits()
    DL = DataListLoader(ana.kFold["k-1"]["train"], batch_size=10)

    fl = []
    for k in range(100):
        t = time.time()
        for x, i in zip(DL, range(len(DL))):
            x = ana.BatchTheseHashes(x, i, ana.Device)
        fl.append(time.time() - t)
        if k == 0:
            continue
        assert fl[0] > fl[-1]
    assert len(fl) != 0
    clean_dir()


#def test_multicache_event():
#
#    ev1 = EventEx()
#    ev2 = EventOther()
#    print(ev1 == ev2)
#    print(ev1.__name__())
#    exit()
#
#
#    ana_ex = Analysis(smpl)
#    ana_ex.ProjectName = "Project"
#    ana_ex.Event = EventEx
#    ana_ex.EventCache = True
#    ana_ex.Launch()
#    events_ex = []
#    for i in ana_ex: events_ex.append(i)
#
#    ana_ot = Analysis(smpl)
#    ana_ot.ProjectName = "Project"
#    ana_ot.Event = EventOther
#    ana_ot.EventCache = True
#    ana_ot.Launch()
#    events_ot = []
#    for i in ana_ot: events_ot.append(i)
#
#    ana_ex = Analysis(smpl)
#    ana_ex.ProjectName = "Project"
#    ana_ex.Event = EventEx
#    ana_ex.EventCache = True
#    ana_ex.Launch()
#
#    ana_ot = Analysis(smpl)
#    ana_ot.ProjectName = "Project"
#    ana_ot.Event = EventOther
#    ana_ot.EventCache = True
#    ana_ot.Launch()
#
#    ana_sum = ana_ot + ana_ex
#    events = []
#    for i in ana_sum: events.append(i)
#    print(len(events))
#    print(len(events_ex))
#    print(len(events_ot))

if __name__ == "__main__":
    test_normal()
    #test_quant()
    
    #test_multicache_event()
    pass




