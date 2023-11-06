from AnalysisG.Generators import GraphGenerator
from AnalysisG.Generators import EventGenerator
from AnalysisG.Events import Event
from AnalysisG.Events import GraphChildren
from examples.Graph import DataGraph
from examples.Event import EventEx
from AnalysisG.Tools import Code

smpl = "./samples/"
Files = {
    smpl + "sample1": ["smpl1.root"],
    smpl + "sample2": ["smpl1.root", "smpl2.root", "smpl3.root"],
}


def fx_edge(a, b):
    return (a + b).Mass

def fx_node(a):
    return a.Mass

def fx_g(ev):
    return ev.met

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

def test_graph_generator():
    root1 = "./samples/sample1/smpl1.root"
    EvtGen = EventGenerator(root1)
    EvtGen.Event = EventEx
    EvtGen.Threads = 12
    EvtGen.Chunks = 1000
    EvtGen.MakeEvents()

    gr = DataGraph()
    gr.AddGraphFeature(fx_graph, "Failed")
    gr.AddGraphFeature(fx_mev, "mev")
    gr.AddNodeFeature(fx_pmu, "pmu")
    gr.AddEdgeTruthFeature(fx_custom_topology, "topo")
    gr.AddEdgeFeature(fx_edge, "Mass")
    gr.SetTopology(fx_custom_topology)
    gr.AddPreSelection(fx_prefilter)

    GrGen = GraphGenerator(EvtGen)
    GrGen.Graph = gr
    GrGen.Threads = 1
    GrGen.Chunks = 1000
    GrGen.MakeGraphs()
    assert len(GrGen.ShowLength) == 2
    assert "nominal/DataGraph" in GrGen.ShowLength
    assert "nominal/EventEx" in GrGen.ShowLength
    assert "nominal/DataGraph" not in EvtGen.ShowLength

    leng = GrGen.ShowLength
    assert leng["nominal/DataGraph"] == leng["nominal/EventEx"]
    GrGen = GraphGenerator(EvtGen)
    GrGen.Graph = gr
    GrGen.Threads = 1
    GrGen.Chunks = 10
    GrGen.EventStop = 10
    GrGen.MakeGraphs()
    assert len(GrGen.ShowLength) == 2
    assert "nominal/DataGraph" in GrGen.ShowLength
    assert "nominal/EventEx" in GrGen.ShowLength
    assert "nominal/DataGraph" not in EvtGen.ShowLength
    leng = GrGen.ShowLength
    assert leng["nominal/DataGraph"] == 10

    GrGen = GraphGenerator(EvtGen)
    GrGen.Graph = gr
    GrGen.Threads = 1
    GrGen.Chunks = 10
    GrGen.MakeGraphs()
    GrGen.GraphName = "DataGraph"
    GrGen.EventName = "EventEx"

    x = []
    for i in GrGen:
        assert i.edge_index is not None
        x.append(i)
        assert isinstance(i.Topology, list)
        assert len(i.Tops) != 0
        for t in i.Particles:
            assert t.px != 0
            assert t.pt != 0
            assert t.pt is not None
        assert "DAOD" in i.ROOT
        assert len(i.Errors) == 1
        assert i.N_pmu is not None
        assert i.GraphName == "DataGraph"
    assert len(x) == GrGen.ShowLength["nominal/EventEx"]

    for i in range(10):
        Gr = GraphGenerator(GrGen)
        Gr.Graph = gr
        Gr.Threads = 2
        Gr.Chunks = 100
        Gr.MakeGraphs()
        GrGen += Gr
    data, event = list(GrGen.ShowLength.values())
    assert data == event

def test_graph_inputs():
    root1 = "./samples/sample1/smpl1.root"
    EvtGen = EventGenerator(root1)
    EvtGen.Event = EventEx
    EvtGen.Threads = 4
    EvtGen.Chunks = 1000
    EvtGen.MakeEvents()

    GrGen = GraphGenerator(EvtGen)
    GrGen.AddGraphFeature(fx_graph, "Failed")
    GrGen.AddGraphTruthFeature(fx_mev, "mev")
    GrGen.AddNodeFeature(fx_pmu, "pmu")
    GrGen.AddNodeTruthFeature(fx_pmu, "pmu")
    GrGen.AddEdgeFeature(fx_edge, "Mass")
    GrGen.AddEdgeTruthFeature(fx_custom_topology, "topo")
    GrGen.AddTopology(fx_custom_topology)
    GrGen.AddPreSelection(fx_prefilter)
    GrGen.Graph = DataGraph
    GrGen.Threads = 1
    GrGen.Chunks = 1000
    GrGen.MakeGraphs()
    x = []
    for ev in GrGen:
        assert ev.edge_index is not None
        x.append(ev)
        assert isinstance(ev.Topology, list)
        assert ev.Tops is not None
        assert len(ev.Tops) != 0
        assert "DAOD" in ev.ROOT
        assert ev.N_T_pmu is not None
    assert len(x) != 0

    x = []
    GrGen.GetEvent = False
    for ev in GrGen:
        assert ev.edge_index is not None
        assert ev.Tops is None
        assert "DAOD" in ev.ROOT
        assert ev.N_T_pmu is not None
        x.append(ev)
    assert len(x) != 0

def test_eventgraph():
    Ev = EventGenerator(Files)
    Ev.Event = Event
    Ev.Threads = 1
    Ev.EventStop = 100
    Ev.MakeEvents()

    for i in Ev:
        assert i.Event
        assert i.hash
        assert i.met
        assert i.met is not None

    Gr = GraphGenerator(Ev)
    Gr.Graph = GraphChildren
    Gr.AddGraphFeature(fx_graph)
    Gr.AddGraphFeature(fx_g)
    Gr.Threads = 1
    Gr.Device = "cuda"
    Gr.MakeGraphs()
    assert Gr["nominal/GraphChildren"] == Ev["nominal/Event"]
    for i in Gr:
        assert i.weight is not None
        assert "G_fx_graph" in i.Errors
        assert "Tensor" == type(i.G_fx_g).__name__
        assert i.Graph
        assert i.hash
        assert i.index >= 0





if __name__ == "__main__":
    test_graph_generator()
    test_graph_inputs()
    test_eventgraph()
