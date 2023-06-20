from AnalysisG.Generators import (
    EventGenerator,
    GraphGenerator,
    SelectionGenerator,
    Analysis,
)
from AnalysisG.Events.Events.Event import Event
from AnalysisG.Events.Graphs.EventGraphs import GraphChildren
from conftest import clean_dir

smpl = "./samples/"
Files = {
    smpl + "sample1": ["smpl1.root"],
    smpl + "sample2": ["smpl1.root", "smpl2.root", "smpl3.root"],
}


def test_event_generator():
    root1 = "./samples/sample1/smpl1.root"

    EvtGen = EventGenerator({root1: []})
    EvtGen.EventStop = 50
    EvtGen.EventStart = 10
    EvtGen.Event = Event
    EvtGen.Threads = 1
    EvtGen.MakeEvents
    lst = {}
    for i in EvtGen:
        lst[i.hash] = i
    assert len(lst) == 40

    EvtGen_ = EventGenerator({root1: []})
    EvtGen_.EventStop = 50
    EvtGen_.EventStart = 10
    EvtGen_.Event = Event
    EvtGen_.Threads = 2
    EvtGen_.MakeEvents
    lst_ = {}
    for i in EvtGen_:
        lst_[i.hash] = i
    assert len(lst_) == len(lst)
    for i in lst_:
        ev_, ev = lst_[i], lst[i]
        sum([t_ == t for t_, t in zip(ev_.Tops, ev.Tops)]) == len(ev.Tops)
        for t_, t in zip(ev_.Tops, ev.Tops):
            for c_, c in zip(t_.Children, t.Children):
                assert c_ == c

        assert len(ev_.TopChildren) == len(ev.TopChildren)
        for t_, t in zip(ev_.TopChildren, ev.TopChildren):
            assert t_ == t

        assert len(ev_.TruthJets) == len(ev.TruthJets)
        for tj_, tj in zip(ev_.TruthJets, ev.TruthJets):
            assert tj_ == tj

        assert len(ev_.DetectorObjects) == len(ev.DetectorObjects)
        for tj_, tj in zip(ev_.DetectorObjects, ev.DetectorObjects):
            assert tj_ == tj
    clean_dir()


def test_event_generator_more():
    print("")
    EvtGen = EventGenerator(Files)
    EvtGen.EventStop = 1000
    EvtGen.EventStart = 50
    EvtGen.Event = Event
    EvtGen.MakeEvents
    assert len(EvtGen) != 0
    tmp = []
    for event in EvtGen:
        assert event == EvtGen[event.hash]
        tmp.append(event)
    assert len(EvtGen) == len(tmp)
    clean_dir()


def test_event_generator_merge():
    f = list(Files)
    File0 = {f[0]: [Files[f[0]][0]]}
    File1 = {f[1]: [Files[f[1]][1]]}

    _Files = {}
    _Files.update(File0)
    _Files.update(File1)

    ev0 = EventGenerator(File0)
    ev0.Event = Event
    ev0.MakeEvents

    ev1 = EventGenerator(File1)
    ev1.Event = Event
    ev1.MakeEvents

    combined = EventGenerator(_Files)
    combined.Event = Event
    combined.MakeEvents

    Object0 = {}
    for i in ev0:
        Object0[i.hash] = i

    Object1 = {}
    for i in ev1:
        Object1[i.hash] = i

    ObjectSum = {}
    for i in combined:
        ObjectSum[i.hash] = i

    assert len(ObjectSum) == len(Object0) + len(Object1)
    assert len(combined) == len(ev0) + len(ev1)

    for i in Object0:
        assert ObjectSum[i] == Object0[i]
    for i in Object1:
        assert ObjectSum[i] == Object1[i]

    combined = ev0 + ev1
    ObjectSum = {}
    for i in combined:
        ObjectSum[i.hash] = i
    for i in Object0:
        assert ObjectSum[i] == Object0[i]
    for i in Object1:
        assert ObjectSum[i] == Object1[i]

    def EventGen_(Dir, Name):
        Ana = Analysis()
        Ana.ProjectName = "Project"
        Ana.InputSample(Name, Dir)
        Ana.EventCache = True
        Ana.Event = Event
        Ana.Threads = 10
        Ana.EventStart = 0
        Ana.EventStop = 10
        Ana.Launch

        return Ana

    ev1 = EventGen_(File0, "Top")
    for i in ev1:
        assert i.Event
    ev2 = EventGen_(File1, "Tops")
    for i in ev2:
        assert i.Event
    ev1 += ev2
    it = 0
    for i in ev1:
        assert ev1[i.hash].hash == i.hash
        it += 1
    ev1.EventCache = False
    assert it == 20

    a_ev = EventGen_(None, None)
    assert len(ev1) == len(a_ev)
    clean_dir()


def _fx(a):
    return 1


def test_eventgraph():
    Ev = EventGenerator(Files)
    Ev.Event = Event
    Ev.Threads = 1
    Ev.EventStop = 100
    Ev.MakeEvents

    for i in Ev:
        assert i.Event
        assert i.hash
        assert i.met

    Gr = GraphGenerator(Ev)
    Gr.EventGraph = GraphChildren
    Gr.AddGraphFeature(_fx)
    Gr.Threads = 2
    Gr.Device = "cuda"
    Gr.MakeGraphs

    assert len(Gr) == len(Ev)
    for i in Gr:
        assert i.Graph
        assert i.hash
        assert i.i >= 0
        assert i.weight
        assert i.G__fx
    clean_dir()


def test_selection_generator():
    from AnalysisG.IO import UnpickleObject
    from examples.ExampleSelection import Example, Example2
    from examples.Event import EventEx

    Ev = EventGenerator(Files)
    Ev.OutputDirectory = "Project"
    Ev.Event = EventEx
    Ev.Threads = 1
    Ev.EventStop = 100
    Ev.MakeEvents

    sel = SelectionGenerator(Ev)
    sel.OutputDirectory = "Project"
    sel += Ev
    sel.Threads = 2
    sel.AddSelection("Example", Example)
    sel.AddSelection("Example2", Example2)
    sel.MergeSelection("Example2")
    sel.MakeSelection

    res = UnpickleObject("./Project/Selections/Merged/Example2")
    assert res.CutFlow["Success->Example"] == len(Ev)
    assert len(res.TimeStats) == len(Ev)
    assert len(Ev) * 4 == len(res.Top["Truth"])
    clean_dir()


def test_Analysis():
    Sample1 = {smpl + "sample1": ["smpl1.root"]}
    Sample2 = smpl + "sample2"

    Ana = Analysis()
    Ana.ProjectName = "_Test"
    Ana.InputSample("Sample1", Sample1)
    Ana.InputSample("Sample2", Sample2)
    Ana.PurgeCache = False
    Ana.OutputDirectory = "../test/"
    Ana.EventStop = 100
    assert Ana.Launch == False
    clean_dir()


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
    AnaE.Launch
    assert len([i for i in AnaE]) != 0


def test_analysis_event_nocache_nolaunch():
    AnaE = _template()
    AnaE.Event = Event
    assert len([i for i in AnaE]) != 0


def test_analysis_event_cache():
    AnaE = _template()
    AnaE.Event = Event
    AnaE.EventCache = True
    AnaE.Launch
    assert len([i for i in AnaE if i.Event]) != 0

    AnaE = _template()
    AnaE.EventCache = True
    AnaE.Verbose = 3
    AnaE.Launch

    assert len([i for i in AnaE if i.Event]) != 0
    clean_dir()


def test_analysis_event_cache_diff_sample():
    Ana1 = _template(
        {
            "Name": "sample2",
            "SampleDirectory": smpl + "sample2/" + Files[smpl + "sample2"][1],
        }
    )
    Ana1.Event = Event
    Ana1.EventCache = True
    Ana1.Launch

    assert len([i for i in Ana1]) != 0

    Ana2 = _template(
        {
            "Name": "sample1",
            "SampleDirectory": smpl + "sample1/" + Files[smpl + "sample1"][0],
        }
    )
    Ana2.Event = Event
    Ana2.EventCache = True
    Ana2.Launch

    assert len([i for i in Ana2]) != 0

    AnaE = _template()
    AnaE.Event = Event
    AnaE.EventCache = True

    AnaS = Ana2 + Ana1
    assert len([i for i in AnaE if i.hash not in AnaS]) == 0
    clean_dir()


def test_analysis_data_nocache():
    AnaE = _template()
    AnaE.AddGraphFeature(_fx)
    AnaE.Event = Event
    AnaE.EventGraph = GraphChildren
    AnaE.Launch

    assert len([i for i in AnaE if i.Graph]) != 0


def test_analysis_data_nocache_nolaunch():
    AnaE = _template()
    AnaE.AddGraphFeature(_fx)
    AnaE.Event = Event
    AnaE.EventGraph = GraphChildren

    assert len([i for i in AnaE if i.Graph]) != 0


def test_analysis_data_cache():
    AnaE = _template()
    AnaE.DataCache = True
    AnaE.AddGraphFeature(_fx)
    AnaE.EventGraph = GraphChildren
    AnaE.Event = Event
    AnaE.Launch

    assert len([i for i in AnaE]) != 0

    AnaE = _template()
    AnaE.DataCache = True
    AnaE.Launch

    assert len([i for i in AnaE if i.Graph]) != 0

    clean_dir()


def test_analysis_data_cache_diff_sample():
    Ana1 = _template(
        {
            "Name": "Sample2",
            "SampleDirectory": smpl + "sample2/" + Files[smpl + "sample2"][1],
        }
    )
    Ana1.Event = Event
    Ana1.EventGraph = GraphChildren
    Ana1.AddGraphFeature(_fx)
    Ana1.DataCache = True
    Ana1.Launch

    assert len([i for i in Ana1 if i.Graph]) != 0

    Ana2 = _template(
        {
            "Name": "Sample1",
            "SampleDirectory": smpl + "sample1/" + Files[smpl + "sample1"][0],
        }
    )
    Ana2.Event = Event
    Ana2.EventGraph = GraphChildren
    Ana2.AddGraphFeature(_fx)
    Ana2.DataCache = True
    Ana2.Launch

    assert len([i for i in Ana2 if i.Graph]) != 0

    AnaE = _template()
    AnaE.DataCache = True
    AnaE.Launch

    AnaS = Ana2 + Ana1
    assert len(AnaE) != 0
    assert len(AnaS) != 0
    assert len([i for i in AnaS if i.hash in AnaE]) == len(AnaE)

    clean_dir()


def test_analysis_data_event_cache_diff_sample():
    Ana1 = _template(
        {
            "Name": "Sample2",
            "SampleDirectory": smpl + "sample2/" + Files[smpl + "sample2"][1],
        }
    )
    Ana1.Event = Event
    Ana1.EventCache = True
    Ana1.Launch

    assert len([i for i in Ana1 if i.Event]) != 0

    Ana1 = _template({"Name": "Sample2"})
    Ana1.EventGraph = GraphChildren
    Ana1.AddGraphFeature(_fx)
    Ana1.DataCache = True

    assert len([i for i in Ana1 if i.Graph and i.G__fx[0][0] == 1]) != 0

    Ana2 = _template(
        {
            "Name": "Sample1",
            "SampleDirectory": smpl + "sample1/" + Files[smpl + "sample1"][0],
        }
    )
    Ana2.Event = Event
    Ana2.EventCache = True
    Ana2.Launch

    assert len([i for i in Ana2]) != 0

    Ana2 = _template({"Name": "Sample1"})
    Ana2.EventGraph = GraphChildren
    Ana2.AddGraphFeature(_fx)
    Ana2.DataCache = True
    Ana2.Launch

    assert len([i for i in Ana2 if i.Graph]) != 0

    clean_dir()


if __name__ == "__main__":
    test_event_generator()
    test_event_generator_more()
    test_event_generator_merge()
    test_eventgraph()
    test_selection_generator()
    test_Analysis()
    test_analysis_event_nocache()
    test_analysis_event_nocache_nolaunch()
    test_analysis_event_cache()
    test_analysis_event_cache_diff_sample()
    test_analysis_data_nocache()
    test_analysis_data_nocache_nolaunch()
    test_analysis_data_cache()
    test_analysis_data_cache_diff_sample()
    test_analysis_data_event_cache_diff_sample()
    pass
