from examples.ExampleSelection import Example, Example2
from AnalysisG.Events import Event, GraphChildren
from AnalysisG.Generators import Analysis

smpl = "./samples/"
Files = {
    smpl + "sample1": ["smpl1.root"],
    smpl + "sample2": ["smpl1.root", "smpl2.root", "smpl3.root"],
}

def test_analysis_event_merge():
    def EventGen_(Dir, Name):
        Ana = Analysis()
        Ana.ProjectName = "Project"
        Ana.InputSample(Name, Dir)
        Ana.Event = Event
        Ana.Threads = 1
        Ana.EventStart = 0
        Ana.EventStop = 10
        return Ana

    Analysis().rm("Project")
    F0 = {smpl + "sample1" : ["smpl1.root"]}
    ev1 = EventGen_(F0, "Top")
    ev1.EventCache = True
    for i in ev1:
        assert i.sample_name == "Top"
        assert i.Event
        assert i.Tops is not None
        assert isinstance(i.Tops, list)

    F1 = {smpl + "sample2" : ["smpl1.root"]}
    ev2 = EventGen_(F1, "Tops")
    ev2.EventCache = True
    for i in ev2:
        assert i.sample_name == "Tops"
        assert i.Event
        assert i.Tops is not None
        assert isinstance(i.Tops, list)
        assert i.Event

    ev1 += ev2
    ev1.Tree = "nominal"
    ev1.EventName = "Event"
    ev1.GetEvent = True
    ev1.EventCache = True
    it = 0
    x = {"Tops" : 0, "Top" : 0}
    for i in ev1:
        x[i.sample_name]+=1
        assert ev1[i.hash].hash == i.hash
        it += 1
    assert x["Tops"] == 10
    assert x["Top"] == 10
    assert it == 20

    a_ev = EventGen_(None, None)
    a_ev.EventStop = None
    a_ev.EventCache = True
    it = 0
    x = {"Tops" : 0, "Top" : 0}
    for i in a_ev:
        x[i.sample_name] += 1
        assert a_ev[i.hash].hash == i.hash
        assert isinstance(i.Tops, list)
        it += 1
    assert x["Tops"] == 10
    assert x["Top"] == 10
    assert len(ev1) == len(a_ev)
    a_ev.rm("Project")


def test_analysis_more_samples():
    Sample1 = {smpl + "sample1": ["smpl1.root"]}
    Sample2 = smpl + "sample2"

    ana = Analysis()
    ana.ProjectName = "Project"
    ana.InputSample("Sample1", Sample1)
    ana.InputSample("Sample2", Sample2)
    ana.EventStop = 100
    ana.EventCache = True
    ana.Event = Event
    ana.Launch()
    assert 100 == len(ana)
    ana.rm("Project")


def _template(default=True):
    AnaE = Analysis()
    AnaE.ProjectName = "Project"
    if default == True:
        AnaE.InputSample("Sample1", smpl + "sample1/" + Files[smpl + "sample1"][0])
        AnaE.InputSample("Sample2", smpl + "sample2/" + Files[smpl + "sample2"][1])
    else:
        AnaE.InputSample(**default)
    AnaE.Threads = 2
    AnaE.Verbose = 1
    return AnaE

def test_analysis_event_nocache():
    AnaE = _template()
    AnaE.Event = Event
    AnaE.Launch()
    assert len([i for i in AnaE]) != 0
    AnaE.rm("Project")

def test_analysis_event_nocache_nolaunch():
    AnaE = _template()
    AnaE.Event = Event
    assert len([i for i in AnaE]) != 0
    AnaE.rm("Project")

def test_analysis_event_cache():
    AnaE = _template()
    AnaE.Event = Event
    AnaE.EventCache = True
    AnaE.Launch()
    assert len([i for i in AnaE if i.Event]) != 0

    Ana = _template()
    Ana.EventCache = True
    Ana.EventName = "Event"
    Ana.Verbose = 3
    for i in Ana:
        print(i.Event, i.Tops)
    assert len([i for i in Ana if i.Event and len(i.Tops)]) != 0
    Ana.rm("Project")

def test_analysis_event_cache_diff_sample():
    Ana1 = _template(
        {
            "Name": "sample2",
            "SampleDirectory": smpl + "sample2/" + Files[smpl + "sample2"][1],
        }
    )
    Ana1.Event = Event
    Ana1.EventCache = True
    Ana1.Launch()

    assert len([i for i in Ana1]) != 0

    Ana2 = _template(
        {
            "Name": "sample1",
            "SampleDirectory": smpl + "sample1/" + Files[smpl + "sample1"][0],
        }
    )
    Ana2.Event = Event
    Ana2.EventCache = True
    Ana2.Launch()

    assert len([i for i in Ana2]) != 0

    AnaE = _template()
    AnaE.Event = Event
    AnaE.EventCache = True

    AnaS = Ana2 + Ana1
    AnaS.ProjectName = "Project"
    AnaS.EventName = "Event"
    assert len([i for i in AnaS]) > 0
    assert len([i for i in AnaE]) > 0
    assert len([i for i in AnaE if i.hash not in AnaS]) == 0
    assert len([i for i in AnaS if i.hash not in AnaE]) == 0
    AnaS.rm("Project")



def fx_edge(a, b):
    return (a + b).Mass

def fx_node(a):
    return a.Mass

def fx_graph(ev):
    return ev.NotAFeature

def fx_mev(ev):
    return ev.met

def fx_custom_topology(a, b):
    return a.FromResonance == b.FromResonance == 1

def fx_pmu(a):
    return [a.pt, a.eta, a.phi, a.e]

def fx_prefilter(ev):
    return ev.nJets > 2

def test_analysis_data_nocache():
    AnaE = _template()
    AnaE.AddGraphFeature(fx_graph, "Graph")
    AnaE.AddNodeFeature(fx_pmu, "Pmu")
    AnaE.AddEdgeFeature(fx_edge, "Mass")
    AnaE.AddNodeTruthFeature(fx_node, "Mass")
    AnaE.EventCache = False
    AnaE.DataCache = False
    AnaE.Event = Event
    AnaE.Graph = GraphChildren
    AnaE.Launch()

    for i in AnaE:
        assert i.Graph
        assert type(i.N_T_Mass).__name__ == "Tensor"
        assert i.G_Graph is None
        assert "G_Graph" in i.Errors
        assert type(i.N_Pmu).__name__ == "Tensor"
        assert type(i.E_Mass).__name__ == "Tensor"
    assert len([i for i in AnaE if i.Graph])
    AnaE.rm("Project")

def test_analysis_data_nocache_nolaunch():
    AnaE = _template()
    AnaE.rm("Project")
    AnaE.AddGraphFeature(fx_graph, "Graph")
    AnaE.AddNodeFeature(fx_pmu, "Pmu")
    AnaE.AddEdgeFeature(fx_edge, "Mass")
    AnaE.AddNodeTruthFeature(fx_node, "Mass")
    AnaE.Event = Event
    AnaE.Graph = GraphChildren

    assert len([i for i in AnaE if i.Graph and i.N_Pmu is not None])
    AnaE.rm("Project")

def test_analysis_data_cache():
    AnaE = _template()
    AnaE.DataCache = True
    AnaE.AddGraphFeature(fx_graph, "Graph")
    AnaE.AddNodeFeature(fx_pmu, "Pmu")
    AnaE.AddEdgeFeature(fx_edge, "Mass")
    AnaE.AddNodeTruthFeature(fx_node, "Mass")
    AnaE.Graph = GraphChildren
    AnaE.Event = Event
    AnaE.Launch()

    assert len([i for i in AnaE]) != 0

    AnaE = _template()
    AnaE.DataCache = True
    AnaE.GraphName = "GraphChildren"
    AnaE.Threads = 10
    AnaE.Launch()

    for i in AnaE:
        assert i.Graph
        assert type(i.N_T_Mass).__name__ == "Tensor"
        assert i.G_Graph is None
        assert "G_Graph" in i.Errors
        assert type(i.N_Pmu).__name__ == "Tensor"
        assert type(i.E_Mass).__name__ == "Tensor"
    assert len([i for i in AnaE if i.Graph])
    AnaE.rm("Project")


def test_analysis_data_cache_diff_sample():
    Ana1 = _template(
        {
            "Name": "Sample2",
            "SampleDirectory": smpl + "sample2/" + Files[smpl + "sample2"][1],
        }
    )
    Ana1.Event = Event
    Ana1.Graph = GraphChildren
    Ana1.AddGraphFeature(fx_graph, "Graph")
    Ana1.AddNodeFeature(fx_pmu, "Pmu")
    Ana1.AddEdgeFeature(fx_edge, "Mass")
    Ana1.AddNodeTruthFeature(fx_node, "Mass")
    Ana1.DataCache = True
    Ana1.Launch()

    for i in Ana1:
        assert i.Graph
        assert type(i.N_T_Mass).__name__ == "Tensor"
        assert i.G_Graph is None
        assert "G_Graph" in i.Errors
        assert type(i.N_Pmu).__name__ == "Tensor"
        assert type(i.E_Mass).__name__ == "Tensor"
    assert len([i for i in Ana1 if i.Graph])

    Ana2 = _template(
        {
            "Name": "Sample1",
            "SampleDirectory": smpl + "sample1/" + Files[smpl + "sample1"][0],
        }
    )
    Ana2.Event = Event
    Ana2.Graph = GraphChildren
    Ana2.AddGraphFeature(fx_graph, "Graph")
    Ana2.AddNodeFeature(fx_pmu, "Pmu")
    Ana2.AddEdgeFeature(fx_edge, "Mass")
    Ana2.AddNodeTruthFeature(fx_node, "Mass")
    Ana2.DataCache = True
    Ana2.Launch()

    for i in Ana2:
        assert i.Graph
        assert type(i.N_T_Mass).__name__ == "Tensor"
        assert i.G_Graph is None
        assert "G_Graph" in i.Errors
        assert type(i.N_Pmu).__name__ == "Tensor"
        assert type(i.E_Mass).__name__ == "Tensor"
    assert len([i for i in Ana2 if i.Graph])

    AnaE = _template()
    AnaE.DataCache = True
    AnaE.GraphName = "GraphChildren"
    AnaE.Launch()

    AnaS = Ana2 + Ana1
    AnaS.GraphName = "GraphChildren"
    AnaS.ProjectName = "Project"
    assert len(AnaE)
    assert len(AnaS)

    for i in AnaS:
        assert i.Graph
        assert type(i.N_T_Mass).__name__ == "Tensor"
        assert i.G_Graph is None
        assert "G_Graph" in i.Errors
        assert type(i.N_Pmu).__name__ == "Tensor"
        assert type(i.E_Mass).__name__ == "Tensor"
    assert len([i for i in AnaS if i.hash in AnaE and i.Graph]) == AnaE.ShowLength["nominal/GraphChildren"]
    AnaS.rm("Project")

def test_analysis_data_event_cache_diff_sample():
    Ana1 = _template(
        {
            "Name": "Sample2",
            "SampleDirectory": smpl + "sample2/" + Files[smpl + "sample2"][1],
        }
    )
    Ana1.Event = Event
    Ana1.EventCache = True
    Ana1.Launch()

    assert len([i for i in Ana1 if i.Event])
    del Ana1

    Ana1 = _template({"Name": "Sample2"})
    Ana1.Graph = GraphChildren
    Ana1.AddGraphFeature(fx_graph, "Graph")
    Ana1.AddNodeFeature(fx_pmu, "Pmu")
    Ana1.AddEdgeFeature(fx_edge, "Mass")
    Ana1.AddNodeTruthFeature(fx_node, "Mass")
    Ana1.DataCache = True
    Ana1.EventName = "Event"
    Ana1.Launch()

    assert len([i for i in Ana1 if i.Graph and i.N_Pmu is not None])
    del Ana1

    Ana2 = _template(
        {
            "Name": "Sample1",
            "SampleDirectory": smpl + "sample1/" + Files[smpl + "sample1"][0],
        }
    )

    Ana2.Event = Event
    Ana2.EventCache = True
    Ana2.Launch()
    assert len([i for i in Ana2 if isinstance(i.Tops, list)])
    del Ana2

    Ana2 = _template({"Name": "Sample1"})
    Ana2.Graph = GraphChildren
    Ana2.AddGraphFeature(fx_graph, "Graph")
    Ana2.AddNodeFeature(fx_pmu, "Pmu")
    Ana2.AddEdgeFeature(fx_edge, "Mass")
    Ana2.AddNodeTruthFeature(fx_node, "Mass")
    Ana2.DataCache = True
    Ana2.EventName = "Event"
    Ana2.Launch()

    assert len([i for i in Ana2 if i.Graph and i.N_Pmu is not None]) != 0
    Ana2.rm("Project")

def test_analysis_selection_nocache():
    Ana1 = _template()
    Ana1.Event = Event
    Ana1.EventCache = False
    Ana1.AddSelection(Example2)
    Ana1.Launch()
    x = []
    for i in Ana1:
        sel = i.release_selection()
        assert sel.Selection
        assert sel.__name__() == "Example2"
        assert "Truth" in sel.Top
        assert isinstance(sel.Top["Truth"], list)
        assert len(sel.Top["Truth"]) == 4
        assert sel.CutFlow["Selection::Passed"] == 1
        x.append(sel)
    assert len(x)
    Ana1.rm("Project")

def test_analysis_selection_nocache_nolaunch():
    Ana1 = _template()
    Ana1.Event = Event
    Ana1.EventCache = False
    Ana1.AddSelection(Example2)
    x = []
    for i in Ana1:
        sel = i.release_selection()
        assert sel.Selection
        assert sel.__name__() == "Example2"
        assert "Truth" in sel.Top
        assert isinstance(sel.Top["Truth"], list)
        assert len(sel.Top["Truth"]) == 4
        assert sel.CutFlow["Selection::Passed"] == 1
        x.append(sel)
    assert len(x)
    Ana1.rm("Project")

def test_analysis_selection_cache():
    Ana1 = _template()
    Ana1.Event = Event
    Ana1.EventCache = False
    Ana1.AddSelection(Example2)
    Ana1.Launch()

    AnaR = _template({"Name": "Sample1"})
    AnaR.SelectionName = "Example2"
    AnaR.Launch()
    x = []
    for i in AnaR:
        sel = i.release_selection()
        assert sel.Selection
        assert sel.__name__() == "Example2"
        assert "Truth" in sel.Top
        assert isinstance(sel.Top["Truth"], list)
        assert len(sel.Top["Truth"]) == 4
        assert sel.CutFlow["Selection::Passed"] == 1
        x.append(sel)
    assert len(x)
    assert len(AnaR["Example2"]) == len(x)
    AnaR.rm("Project")

if __name__ == "__main__":
    test_analysis_event_merge()
#    test_analysis_more_samples()
#    test_analysis_event_nocache()
#    test_analysis_event_nocache_nolaunch()
#    test_analysis_event_cache()
#    test_analysis_event_cache_diff_sample()
#
#    test_analysis_data_nocache()
#    test_analysis_data_nocache_nolaunch()
#    test_analysis_data_cache()
#    test_analysis_data_cache_diff_sample()
#    test_analysis_data_event_cache_diff_sample()
#
#    test_analysis_selection_nocache()
#    test_analysis_selection_nocache_nolaunch()
#    test_analysis_selection_cache()

