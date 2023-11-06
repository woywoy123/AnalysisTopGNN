from AnalysisG import Analysis
from examples.Event import EventEx
from examples.EventOther import EventOther
from examples.Graph import DataGraph, DataEx

def test_event_flush():

    ana = Analysis()
    ana.Event = EventEx
    ana.InputSample(None, "samples/dilepton/")
    ana.EventCache = True
    ana.ProjectName = "Project"
    ana.Launch()

    for i in ana: break

    hashes = [i.hash for i in ana.makelist()]
    assert len(hashes)
    ana.FlushEvents(hashes)

    ana.EventName = "EventEx"
    ana.GetEvent = True
    assert len(ana.makehashes()["event"])

    ana.GetEvent = False
    assert not len(ana.makehashes()["event"])
    assert not len([i for i in ana.makelist() if i.Event])

    ana.GetEvent = True
    ana.RestoreEvents(sum([i for i in ana.makehashes()["event"].values()], []))

    ana.GetEvent = True
    ana.EventName = "EventEx"
    hashes = [i.Event for i in ana.makelist() if i.Event]
    assert len(hashes)

    hashes = [i.Event for i in ana if i.Event]
    assert len(hashes)

def test_change_event_cache():
    ana = Analysis()
    ana.ProjectName = "Project"
    ana.Event = EventEx
    ana.InputSample(None, "samples/dilepton/")
    ana.EventCache = True
    ana.Launch()
    x = []
    for i in ana: x.append(i)
    assert len(x)


    ana = Analysis()
    ana.ProjectName = "Project"
    ana.Event = EventOther
    ana.InputSample(None, "samples/dilepton/")
    ana.EventCache = True
    ana.Launch()
    y = []
    for i in ana: y.append(i)
    assert len(y)

    diff = {"EventOther": 0, "EventEx": 0}
    ana = Analysis()
    ana.ProjectName = "Project"
    ana.EventCache = True
    ana.EventName = "EventOther"
    for i in ana: diff[i.EventName] += 1

    ana = Analysis()
    ana.ProjectName = "Project"
    ana.EventCache = True
    ana.EventName = "EventEx"
    for i in ana: diff[i.EventName] += 1
    assert diff["EventOther"] == diff["EventEx"]
    ana.rm("Project")

def fx(a, b): return 1

def test_change_graph_cache():
    ana = Analysis()
    ana.Event = EventEx
    ana.InputSample(None, "samples/dilepton/")
    ana.EventCache = True
    ana.ProjectName = "Project"
    ana.Launch()
    x = []
    for i in ana: x.append(i)
    assert len(x)

    ana = Analysis()
    ana.Event = EventOther
    ana.InputSample(None, "samples/dilepton/")
    ana.EventCache = True
    ana.ProjectName = "Project"
    ana.Launch()
    y = []
    for i in ana: y.append(i)
    assert len(y)

    diff = {"DataEx":0, "DataGraph":0}
    ana = Analysis()
    ana.ProjectName = "Project"
    ana.EventCache = True
    ana.DataCache = True
    ana.EventName = "EventOther"
    ana.AddEdgeFeature(fx)
    ana.Tree = "nominal"
    ana.Graph = DataEx
    for i in ana: diff[i.GraphName] += 1

    ana = Analysis()
    ana.ProjectName = "Project"
    ana.EventCache = True
    ana.DataCache = True
    ana.EventName = "EventEx"
    ana.Tree = "nominal"
    ana.AddEdgeFeature(fx)
    ana.Graph = DataGraph
    for i in ana: diff[i.GraphName] += 1
    assert diff["DataEx"] == diff["DataGraph"]

    diff = {"DataEx":0, "DataGraph":0}
    ana = Analysis()
    ana.ProjectName = "Project"
    ana.DataCache = True
    ana.GraphName = "DataGraph"
    for i in ana:diff[i.GraphName] += 1

    ana = Analysis()
    ana.ProjectName = "Project"
    ana.DataCache = True
    ana.GraphName = "DataEx"
    for i in ana:diff[i.GraphName] += 1

    assert diff["DataEx"] == diff["DataGraph"]
    assert diff["DataEx"] != 0
    ana.rm("Project")

if __name__ == "__main__":
    test_event_flush()
    test_change_event_cache()
    test_change_graph_cache()
