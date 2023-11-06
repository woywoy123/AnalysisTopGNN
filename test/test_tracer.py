from AnalysisG._cmodules.SampleTracer import SampleTracer
from AnalysisG.SampleTracer import SampleTracer
from AnalysisG.Templates import EventTemplate
from AnalysisG.Templates import ParticleTemplate
from AnalysisG.IO import UpROOT
import pickle
import shutil
import psutil
import os


class Particle(ParticleTemplate):
    def __init__(self):
        ParticleTemplate.__init__(self)
        self.pt = self.Type + "_pt"
        self.eta = self.Type + "_eta"
        self.phi = self.Type + "_phi"
        self.e = self.Type + "_e"


class Top(Particle):
    def __init__(self):
        self.Type = "top"
        Particle.__init__(self)


class Children(Particle):
    def __init__(self):
        self.Type = "children"
        Particle.__init__(self)


class Event(EventTemplate):
    def __init__(self):
        EventTemplate.__init__(self)
        self.Objects = {"top": Top, "Children": Children()}
        self.index = "eventNumber"
        self.weight = "weight_mc"
        self.Trees = ["nominal", "truth"]
        self.met_phi = "met_phi"
        self.CommitHash = "..."
        self.deprecated = False


def test_tracer_addEvent():
    tr = SampleTracer()

    root1 = os.path.abspath("./samples/sample1/smpl1.root")
    root2 = os.path.abspath("./samples/sample1/smpl2.root")
    ev = Event()
    ev.__getleaves__()

    io = UpROOT([root1, root2])
    io.EnablePyAMI = False
    io.Trees = ev.Trees
    io.Leaves = ev.Leaves

    hashes = {}
    roothashes = {}
    len_nom, len_tru = 0, 0
    for i in io:
        if "nominal/eventNumber" in i: len_nom += 1
        if "truth/eventNumber" in i: len_tru += 1
        root, index, meta = i["ROOT"], i["EventIndex"], i["MetaData"]
        trees = ev.__compiler__(i)
        for t in trees:
            t.CompileEvent()
            tr.AddEvent(t, meta)
        hashes.update({p.hash: p for p in trees})
        if root not in roothashes: roothashes[root] = []
        roothashes[root] += [p.hash for p in trees]

    assert len_tru + len_nom == len(tr)
    tr.Tree = "nominal"
    tr.EventName = "Event"
    assert len_nom == len(tr)

    tr.Tree = "truth"
    tr.EventName = "Event"
    assert len_tru == len(tr)

    tr.Tree = ""
    tr.EventName = "Event"
    assert len_tru + len_nom == len(tr)


    # Test iterator
    tr.Tree = "truth"
    tr.EventName = "Event"
    tr.Threads = 12
    tr.GetEvent = True
    for i in tr: assert i.hash == hashes[i.hash].hash

    # Test Getter Functions
    for i in hashes:
        assert tr[i].Tree == hashes[i].Tree
        assert tr[i].hash == hashes[i].hash

    # Test if hashes are in tracer
    for i in hashes: assert i in tr

    assert "hello" not in tr
    assert root1 in tr
    assert len(tr[root1]) > 0

    for r in roothashes:
        inpt = {i.hash : i for i in tr[r]}
        for hsh in roothashes[r]: assert inpt[hsh].original_input == r
        assert len(inpt) > 0



def EventMaker(root):
    ev = Event()
    ev.__getleaves__()
    io = UpROOT(root)
    io.Trees = ev.Trees
    io.Leaves = ev.Leaves
    out = {}
    n_events = {}
    for i in io:
        root, index, meta = i["ROOT"], i["EventIndex"], i["MetaData"]
        trees = ev.__compiler__(i)
        for i in trees:
            i.CompileEvent()
            if i.Tree not in n_events: n_events[i.Tree] = 0
            n_events[i.Tree] += 1
            if i.hash not in out: out[i.hash] = {}
            out[i.hash][i.Tree] = {"Event" : i, "MetaData" : meta}
    return (out, n_events)

def test_tracer_operators():
    root1 = os.path.abspath("./samples/sample1/smpl1.root")
    root2 = os.path.abspath("./samples/sample1/smpl2.root")

    t1_event, n1_events = EventMaker(root1)

    tr1 = SampleTracer()
    tr1.AddEvent(t1_event)
    l1 = len(tr1)
    assert l1 == sum([k for k in n1_events.values()])
    tr1.Tree = "nominal"
    tr1.EventName = "Event"
    tr1.GetAll = False

    # not set the event/tree, should default to nominal
    nominal_n = {i : t1_event[i.hash]["nominal"]["Event"] for i in tr1}
    assert len(nominal_n) == n1_events["nominal"]

    # assign tree 
    tr1.Tree = "truth"
    truth_n = {i : t1_event[i.hash]["truth"]["Event"] for i in tr1}
    assert len(truth_n) == n1_events["truth"]

    tr1.Tree = "nominal"
    nom_n = {i : t1_event[i.hash]["nominal"]["Event"] for i in tr1}
    assert len(nom_n) == n1_events["nominal"]

    # Check for particle and event properties
    for i, j in nom_n.items():
        assert i.hash == j.hash
        assert i.Tree == j.Tree
        t1, t2 = i.top, j.top
        assert len(t1) == len(t2)

        # check if truth tops are actually not nulls
        assert set([l for l in t2.values()]) != 1


        delta = []
        for t in t2:
            assert t1[t].Type == t2[t].Type
            assert t1[t].hash == t2[t].hash
            assert t1[t].pt == t2[t].pt
            assert t1[t].Mass == t2[t].Mass

            # check the deltaR
            delta += [t1[k].DeltaR(t2[t]) for k in range(len(t2))]
        assert len(set(delta)) != 1

        t1, t2 = i.Children, j.Children
        assert len(t1) == len(t2)

        # check if truth children are actually not nulls
        assert set([l for l in t2.values()]) != 1

        for t in t2:
            assert t1[t].Type == t2[t].Type
            assert t1[t].hash == t2[t].hash
            assert t1[t].pt == t2[t].pt
            assert t1[t].Mass == t2[t].Mass

    t2_event, n2_events = EventMaker(root2)
    tr2 = SampleTracer()
    tr2.AddEvent(t2_event)
    l2 = len(tr2)


    # reset tracers 
    tr1.Tree = ""
    tr2.Tree = ""
    trsum = tr1 + tr2
    lsum = len(trsum)

    assert lsum == l2 + l1
    assert len(tr1) == l1
    assert len(tr2) == l2

    trsum.Tree = "nominal"
    trsum.EventName = "Event"
    trsum.GetEvent = True
    for i in nom_n.values():
        j = trsum[i.hash]
        assert i.hash == j.hash
        assert i.Tree == j.Tree
        t1, t2 = i.top, j.top
        assert len(t1) == len(t2)

        # check if truth tops are actually not nulls
        assert set([l for l in t2.values()]) != 1

        delta = []
        for t in t2:
            assert t1[t].Type == t2[t].Type
            assert t1[t].hash == t2[t].hash
            assert t1[t].pt == t2[t].pt
            assert t1[t].Mass == t2[t].Mass

            # check the deltaR
            delta += [t1[k].DeltaR(t2[t]) for k in range(len(t2))]
        assert len(set(delta)) != 1

        t1, t2 = i.Children, j.Children
        assert len(t1) == len(t2)

        # check if truth children are actually not nulls
        assert set([l for l in t2.values()]) != 1

        for t in t2:
            assert t1[t].Type == t2[t].Type
            assert t1[t].hash == t2[t].hash
            assert t1[t].pt == t2[t].pt
            assert t1[t].Mass == t2[t].Mass

    for i in tr1: assert trsum[i.hash]
    for i in tr2: assert trsum[i.hash]

    del tr1
    del tr2

    out = []
    for i in trsum: out.append(i.hash)

    assert len(out) == n2_events["nominal"] + n1_events["nominal"]


def test_tracer_hdf5():
    root1 = os.path.abspath("./samples/sample1/smpl1.root")
    root2 = os.path.abspath("./samples/sample1/smpl2.root")

    tr1 = SampleTracer()
    tr1.OutputDirectory = "Project"
    tr1.AddEvent(EventMaker(root1)[0])
    l1 = len(tr1)

    tr2 = SampleTracer()
    tr2.OutputDirectory = "Project"
    tr2.AddEvent(EventMaker(root2)[0])
    l2 = len(tr2)

    tr1.DumpEvents()
    tr1.DumpTracer()

    tr2.DumpEvents()
    tr2.DumpTracer()

    s = SampleTracer()
    s.OutputDirectory = "Project"
    s.EventCache = True
    s.RestoreTracer()
    s.RestoreEvents()

    for i in tr1["Event"]: break
    print(len(s[i.ROOT]), len(tr1))
    assert len(s[i.ROOT]) == len(tr1)

    for i in tr2["Event"]: break
    assert len(s[i.ROOT]) == len(tr2)

    for i in tr1: assert s[i.hash]
    for i in tr2: assert s[i.hash]

    trsum = tr1 + tr2
    for i in s: assert trsum[i.hash]

    del s
    del trsum

    for i in tr1: assert i.hash
    for i in tr2: assert i.hash
    del tr1
    del tr2

    # Check for memory leaks
    mem = 0
    for i in range(10):
        s = SampleTracer()
        s.OutputDirectory = "Project"
        s.EventCache = True
        s.RestoreTracer()
        s.RestoreEvents()
        k = sum([s for l in range(10)])
        if mem == 0: mem = psutil.virtual_memory().percent
        assert psutil.virtual_memory().percent - mem < 4
        assert s.ShowLength["nominal/Event"] == 165
        del s

    try: shutil.rmtree("Project")
    except: pass


if __name__ == "__main__":
    #test_tracer_addEvent()
    test_tracer_operators()
    #test_tracer_hdf5()
    pass
