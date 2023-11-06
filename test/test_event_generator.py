from AnalysisG.Generators import EventGenerator
from AnalysisG.Events import Event

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
    EvtGen.MakeEvents()
    lst = {}
    for i in EvtGen: lst[i.hash] = i
    assert len(lst) == 40

    EvtGen_ = EventGenerator({root1: []})
    EvtGen_.EventStop = 50
    EvtGen_.EventStart = 10
    EvtGen_.Event = Event
    EvtGen_.MakeEvents()
    EvtGen_.Threads = 2
    lst_ = {}
    for i in EvtGen_: lst_[i.hash] = i
    assert len(lst_) == len(lst)
    for i in lst_:
        ev_, ev = lst_[i], lst[i]
        assert len(ev_.Tops) == len(ev.Tops)
        sum([t_.pt == t.pt for t_, t in zip(ev_.Tops, ev.Tops)]) == len(ev.Tops)
        for t_, t in zip(ev_.Tops, ev.Tops):
            for c_, c in zip(t_.Children, t.Children): assert c_ == c

        assert len(ev_.TopChildren) == len(ev.TopChildren)
        for t_, t in zip(ev_.TopChildren, ev.TopChildren): assert t_ == t

        assert len(ev_.TruthJets) == len(ev.TruthJets)
        for tj_, tj in zip(ev_.TruthJets, ev.TruthJets): assert tj_ == tj

        assert len(ev_.DetectorObjects) == len(ev.DetectorObjects)
        for tj_, tj in zip(ev_.DetectorObjects, ev.DetectorObjects): assert tj_ == tj


def test_event_generator_more():
    print("")
    EvtGen = EventGenerator(Files)
    EvtGen.EventStop = 1000
    EvtGen.EventStart = 50
    EvtGen.Event = Event
    EvtGen.MakeEvents()
    assert len(EvtGen) != 0
    tmp = []
    for event in EvtGen:
        assert event == EvtGen[event.hash]
        tmp.append(event)
    assert len(EvtGen) == len(tmp)

def test_event_generator_merge():
    f = list(Files)
    File0 = {f[0]: [Files[f[0]][0]]}
    File1 = {f[1]: [Files[f[1]][1]]}

    _Files = {}
    _Files.update(File0)
    _Files.update(File1)

    ev0 = EventGenerator(File0)
    ev0.Event = Event
    ev0.MakeEvents()

    ev1 = EventGenerator(File1)
    ev1.Event = Event
    ev1.MakeEvents()

    combined = EventGenerator(_Files)
    combined.Event = Event
    combined.MakeEvents()

    Object0 = {}
    for i in ev0: Object0[i.hash] = i
    Object1 = {}
    for i in ev1: Object1[i.hash] = i

    ObjectSum = {}
    for i in combined: ObjectSum[i.hash] = i

    assert len(Object0) > 0
    assert len(Object1) > 0
    assert len(ObjectSum) > 0

    assert len(ObjectSum) == len(Object0) + len(Object1)
    assert len(combined) == len(ev0) + len(ev1)

    for i in Object0: assert ObjectSum[i] == Object0[i]
    for i in Object1: assert ObjectSum[i] == Object1[i]

    combined = ev0 + ev1
    ObjectSum = {}
    for i in combined: ObjectSum[i.hash] = i
    for i in Object0: assert ObjectSum[i] == Object0[i]
    for i in Object1: assert ObjectSum[i] == Object1[i]

if __name__ == "__main__":
    test_event_generator()
    test_event_generator_more()
    test_event_generator_merge()
