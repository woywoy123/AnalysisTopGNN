from examples.ExampleSelection import Example, Example2
from AnalysisG.Generators import SelectionGenerator
from AnalysisG.Generators import EventGenerator
from AnalysisG.IO import nTupler, UpROOT
from examples.Event import EventEx

smpl = "./samples/"
Files = {
    smpl + "sample1": ["smpl1.root"],
    smpl + "sample2": ["smpl1.root", "smpl2.root", "smpl3.root"],
}
def template():
    EvtGen = EventGenerator(Files)
    EvtGen.EventStop = 100
    EvtGen.EventStart = 10
    EvtGen.Event = EventEx
    EvtGen.Threads = 1
    EvtGen.MakeEvents()
    return EvtGen

def selection_template():
    ev = template()
    sel = SelectionGenerator(ev)
    sel.ProjectName = "Project"
    sel.Threads = 2
    sel.AddSelection(Example)
    sel.AddSelection(Example2)
    sel.MakeSelections()
    sel.DumpSelections()
    sel.DumpTracer()

def test_selection_generator():
    ev = template()
    hsh = {}
    for i in ev: hsh[i.hash] = i

    sel = SelectionGenerator(ev)
    sel.Threads = 2
    sel.AddSelection(Example)
    sel.AddSelection(Example2)
    sel.MakeSelections()
    sel.GetEvent = False
    x = []
    assert "nominal/EventEx" in sel.ShowLength
    assert "nominal/Example" in sel.ShowLength
    assert "nominal/Example2" in sel.ShowLength
    for i in sel:
        assert i.SelectionName == "Example"
        assert "Truth" in i.Top
        assert i.hash in hsh
        e = hsh[i.hash]
        assert e.ROOT == i.ROOT
        assert e.index == i.index
        x.append(i)
    assert len(x) >= 90
    sel.rm("Project")

def test_selection_ntupler():
    selection_template()

    nt = nTupler()
    nt.ProjectName = "Project"
    nt.This("Example2 -> ", "nominal")
    nt.This("Example", "nominal")
    nt.This("Bogus" , "nominal")
    key1, key2 = "nominal.Example", "nominal.Example2"
    x = []
    for i in nt:
        assert key1 in i
        assert key2 in i
        assert i[key1].__name__() == "Example"
        assert i[key2].__name__() == "Example2"
        assert "Truth" in i[key1].Top
        assert isinstance(i[key1].Top["Truth"], list)
        assert len(i[key1].Top["Truth"]) == 4
        assert "nominal.Bogus" not in i
        x.append(i)
    assert len(x) == 90
    nt.rm("Project")


def test_selection_merge():
    selection_template()
    n = nTupler()
    n.ProjectName = "Project"
    n.This("Example2 -> ", "nominal")
    x = n.merged()
    assert "nominal.Example2" in x
    sel = x["nominal.Example2"]
    assert sel.Tree == "nominal"
    assert "Truth" in sel.Top
    assert len(sel.Top["Truth"]) == 360
    n.rm("Project")

def test_selection_root():
    path = "./Project/"
    selection_template()

    # Single case
    test = []
    n = nTupler()
    n.ProjectName = "Project"
    n.This("Example2 -> Top", "nominal")
    for i in n: test.append(i["nominal.Example2"].Top)
    assert len(test) == 90
    n.MakeROOT("./Project/Example")

    test = []
    x = UpROOT(path + "Example.root")
    x.Trees = ["nominal_Example2"]
    x.Leaves = ["Top_Truth"]
    for i in x: test += i["nominal_Example2/Top_Truth"].tolist()
    assert len(test) == 360
    x.rm(path + "Example.root")

    # Mutiple Cases
    test = []
    n = nTupler()
    n.ProjectName = "Project"
    n.This("Example2 -> Top", "nominal")
    n.This("Example2 -> CutFlow", "nominal")
    n.This("Example2 -> AverageTime", "nominal")
    n.This("Example -> AverageTime", "nominal")
    n.This("Example2 -> Children -> Test -> t", "nominal")
    n.This("Example2 -> Children -> Truth", "nominal")
    for i in n: test.append(i)
    assert len(test) == 90
    n.MakeROOT(path + "Example2.root")

    test2 = []
    x = UpROOT(path + "Example2.root")
    x.Trees = ["nominal_Example2"]
    x.Leaves = ["Children_Test_t"]
    for i in x: test2.append(i["nominal_Example2/Children_Test_t"])
    assert sum(test2) == 90

    test2 = []
    x = UpROOT(path + "Example2.root")
    x.Trees = ["nominal_Example2"]
    x.Leaves = ["AverageTime"]
    for i in x: test2.append(i["nominal_Example2/AverageTime"])
    assert len(test2) == 90

    test2 = []
    x = UpROOT(path + "Example2.root")
    x.Trees = ["nominal_Example2_CutFlow"]
    x.Leaves = ["Selection::Passed"]
    for i in x: test2.append(i["nominal_Example2_CutFlow/Selection::Passed"])
    assert len(test2) == 90

    test2 = []
    x = UpROOT(path + "Example2.root")
    x.Trees = ["nominal_Example"]
    x.Leaves = ["event_index"]
    for i in x: test2.append(i["nominal_Example/event_index"])
    assert len(test2) == 90
    x.rm("Project")


if __name__ == "__main__":
    test_selection_generator()
    test_selection_ntupler()
    test_selection_merge()
    test_selection_root()
