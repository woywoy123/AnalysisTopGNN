from AnalysisG.Generators import EventGenerator
from examples.ExampleSelection import Example, Example2
from examples.Event import EventEx

smpl = "./samples/"
Files = {
    smpl + "sample1": ["smpl1.root"],
#    smpl + "sample2": ["smpl1.root", "smpl2.root", "smpl3.root"],
}

def template():
    EvtGen = EventGenerator(Files)
    EvtGen.EventStop = 50
    EvtGen.EventStart = 10
    EvtGen.Event = EventEx
    EvtGen.Threads = 1
    EvtGen.MakeEvents()
    return EvtGen


def test_selection_code():
    Evnt = template()
    x = Example()
    assert x.__scrapecode__() is not None
    for i in Evnt: x.__processing__(i)
    assert "Selection::Passed" in x.CutFlow
    assert "Strategy::Example::Passed" in x.CutFlow

    # test the arithmetic
    lst = []
    for i in Evnt:
        lst.append(Example())
        lst[-1].__processing__(i)
    out = sum(lst)
    assert out.CutFlow == x.CutFlow

if __name__ == "__main__":
    test_selection_code()
