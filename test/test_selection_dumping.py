from AnalysisG.Generators import EventGenerator, SelectionGenerator
from examples.ExampleSelection import Example, Example2
from examples.Event import EventEx
from AnalysisG import Analysis
from AnalysisG.IO import nTupler, UpROOT
from conftest import clean_dir
from time import sleep
import uproot

path = "Project/Selections/Merged/"
smpl = "./samples/"
Files = {
    smpl + "sample1": ["smpl1.root"],
    smpl + "sample2": ["smpl1.root", "smpl2.root", "smpl3.root"],
}

def _template(merge = True):
    Ev = EventGenerator(Files)
    Ev.OutputDirectory = "Project"
    Ev.Event = EventEx
    Ev.Threads = 1
    Ev.EventStop = 100
    Ev.MakeEvents()
    x = 0
    for i in Ev: x+=1
    assert x == 100

    sel = SelectionGenerator(Ev)
    sel.OutputDirectory = "Project"
    sel += Ev
    sel.Threads = 2
    sel.AddSelection("Example", Example)
    sel.AddSelection("Example2", Example2)
    if not merge: return sel.MakeSelection()
    sel.MergeSelection("Example2")
    sel.MergeSelection("Example")
    sel.MakeSelection()

def test_selection_generator():
    _template()
    n = nTupler(path)
    n.This("Example2 -> ", "nominal")
    x = []
    for i in n:
        assert i.__class__.__name__ == "Example2"
        assert i.Tree == "nominal"
        assert "Truth" in i.Top
        assert isinstance(i.Top["Truth"], list)
        assert len(i.Top["Truth"]) == 4
        x.append(i)
    assert len(x) == 100
    n.rm(path)

def test_selection_merge():
    _template()
    n = nTupler(path)
    n.This("Example2 -> ", "nominal")
    x = n.merged()
    assert "Example2" in x
    sel = x["Example2"]
    assert sel.Tree == "nominal"
    assert "Truth" in sel.Top
    assert len(sel.Top["Truth"]) == 400
    n.rm(path)

def test_selection_not_merged():
    _template(False)
    n = nTupler( "/".join(path.split("/")[:-2])+ "/Example2" )
    n.This("Example2 -> ", "nominal")
    x = n.merged()

    assert "Example2" in x
    sel = x["Example2"]
    assert sel.Tree == "nominal"
    assert "Truth" in sel.Top
    assert len(sel.Top["Truth"]) == 400
    n.rm(path)

def test_selection_root():
    _template()
    # Single case
    test = []
    n = nTupler(path)
    n.This("Example2 -> Top", "nominal")
    for i in n: test.append(i.Top)
    assert len(test) == 100
    n.Write()

    test = []
    x = UpROOT(path + "Example2.root")
    x.Trees = ["nominal_Top"]
    x.Branches = ["Truth"]
    for i in x: test.append(i["nominal_Top/Truth"])
    assert len(test) == 400
    x.rm(path + "Example2.root")

    # Mutiple Cases
    test = []
    n = nTupler(path)
    n.rm(path + "Example.root")
    n.rm(path + "Example2.root")
    n.This("Example2 -> Top", "nominal")
    n.This("Example2 -> CutFlow", "nominal")
    n.This("Example2 -> TimeStats", "nominal")
    n.This("Example -> TimeStats", "nominal")
    n.This("Example2 -> Children -> Test -> t", "nominal")
    n.This("Example2 -> Children -> Truth", "nominal")
    for i in n: test.append(i)
    assert len(test) == 200
    n.Write()

    test2 = []
    x = UpROOT(path + "Example2.root")
    x.Trees = ["nominal_Children"]
    x.Branches = ["Test_t"]
    for i in x: test2.append(i[next(iter(i))])
    assert sum(test2) == 100

    test2 = []
    x = UpROOT(path + "Example2.root")
    x.Trees = ["nominal_TimeStats"]
    x.Branches = ["TimeStats"]
    for i in x: test2.append(i[next(iter(i))])
    assert len(test2) == 100

    test2 = []
    x = UpROOT(path + "Example2.root")
    x.Trees = ["nominal_CutFlow"]
    x.Branches = ["Passed-Selection"]
    for i in x: test2.append(i[next(iter(i))])
    assert len(test2) == 1
    assert sum(test2) == 100

    test2 = []
    x = UpROOT(path + "Example2.root")
    x.Trees = ["nominal_CutFlow"]
    x.Branches = ["Rejected-Selection"]
    for i in x: test2.append(i[next(iter(i))])
    assert len(test2) == 1
    assert sum(test2) == 0
    clean_dir()

if __name__ == "__main__":
    test_selection_generator()
    test_selection_merge()
    test_selection_not_merged()
    test_selection_root()

