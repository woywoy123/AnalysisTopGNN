from AnalysisG import Analysis
from AnalysisG.Events import Event, GraphChildren
from AnalysisG.Templates import ApplyFeatures
from AnalysisG.Generators import Optimizer
from torch_geometric.loader import DataListLoader
import torch
import time
from conftest import clean_dir

smpl = "samples/dilepton/"


def test_normal():
    ana = Analysis(smpl)
    ana.Event = Event
    ana.EventCache = True
    ana.Launch
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
    ana.Launch

    ana = Analysis(smpl)
    ana.DataCache = True
    ana.EventGraph = GraphChildren
    ApplyFeatures(ana, "TruthChildren")
    ana.Launch

    ana = Analysis()
    ana.TrainingSize = 50
    ana.kFolds = 10
    ana.Launch

    ana = Optimizer(ana)
    ana.DataCache = True
    ana.Device = "cuda"
    ana._outDir = ana.OutputDirectory + "/Training"
    ana._searchdatasplits
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


if __name__ == "__main__":
    test_normal()
    test_quant()
