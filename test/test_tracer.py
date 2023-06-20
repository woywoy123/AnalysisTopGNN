from AnalysisG.Templates import EventTemplate
from AnalysisG.Templates import ParticleTemplate
from AnalysisG.IO import UpROOT
from AnalysisG.Tracer import SampleTracer
import pickle
import shutil
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
        self.Deprecated = False


def test_tracer_addEvent():
    tr = SampleTracer()

    root1 = os.path.abspath("./samples/sample1/smpl1.root")
    root2 = os.path.abspath("./samples/sample1/smpl2.root")
    ev = Event()
    ev.__interpret__

    io = UpROOT([root1, root2])
    io.Trees = ev.Trees
    io.Leaves = ev.Leaves

    hashes = {}
    roothashes = {}
    for i in io:
        root, index, meta = i["ROOT"], i["EventIndex"], i["MetaData"]
        trees = ev.__compiler__(i)
        for i in trees:
            i.CompileEvent()
        root = meta.thisSet + "/" + meta.thisDAOD
        inpt = {
            i.hash: {
                "pkl": pickle.dumps(i),
                "index": i.index,
                "Tree": i.Tree,
                "ROOT": root,
                "Meta": meta,
            }
            for i in trees
        }
        tr.AddEvent(inpt)
        hashes.update({p.hash: p for p in trees})
        if root not in roothashes:
            roothashes[root] = []
        roothashes[root] += [p.hash for p in trees]
    assert len(io) * 2 == len(tr)

    # Test iterator
    for i in tr:
        assert i.hash == hashes[i.hash].hash

    # Test Getter Functions
    for i in hashes:
        assert tr[i].Tree == hashes[i].Tree
        assert tr[i].hash == hashes[i].hash

    # Test if hashes are in tracer
    for i in hashes:
        assert i in tr

    assert "hello" not in tr
    assert root1 in tr
    assert len(tr[root1]) > 0

    for r in roothashes:
        for hsh in roothashes[r]:
            assert r == tr.HashToROOT(hsh)
    lst = [i for j in range(1000) for i in hashes]

    assert len(hashes) > 0
    assert sum(tr.FastHashSearch(lst).values()) == len(hashes)


def EventMaker(root):
    ev = Event()
    ev.__interpret__
    io = UpROOT(root)
    io.Trees = ev.Trees
    io.Leaves = ev.Leaves
    out = {}
    for i in io:
        root, index, meta = i["ROOT"], i["EventIndex"], i["MetaData"]
        trees = ev.__compiler__(i)
        root = meta.thisSet + "/" + meta.thisDAOD
        for i in trees:
            i.CompileEvent()
        out.update(
            {
                i.hash: {
                    "pkl": pickle.dumps(i),
                    "index": i.index,
                    "Tree": i.Tree,
                    "ROOT": root,
                    "Meta": meta,
                }
                for i in trees
            }
        )
    return out


def test_tracer_operators():
    root1 = os.path.abspath("./samples/sample1/smpl1.root")
    root2 = os.path.abspath("./samples/sample1/smpl2.root")

    tr1 = SampleTracer()
    tr1.AddEvent(EventMaker(root1))
    l1 = len(tr1)

    tr2 = SampleTracer()
    tr2.AddEvent(EventMaker(root2))
    l2 = len(tr2)

    trsum = tr1 + tr2
    lsum = len(trsum)

    assert lsum == l2 + l1
    assert len(tr1) == l1
    assert len(tr2) == l2

    for i in tr1:
        assert trsum[i.hash]
    for i in tr2:
        assert trsum[i.hash]

    del tr1
    del tr2

    assert len([trsum.HashToROOT(i.hash) for i in trsum]) == lsum


def test_tracer_hdf5():
    root1 = os.path.abspath("./samples/sample1/smpl1.root")
    root2 = os.path.abspath("./samples/sample1/smpl2.root")

    tr1 = SampleTracer()
    tr1.OutputDirectory = "Project"
    tr1.AddEvent(EventMaker(root1))
    l1 = len(tr1)

    tr2 = SampleTracer()
    tr2.OutputDirectory = "Project"
    tr2.AddEvent(EventMaker(root2))
    l2 = len(tr2)

    tr1.DumpEvents
    tr2.DumpEvents

    s = SampleTracer()
    s.OutputDirectory = "Project"
    s.EventCache = True
    s.RestoreTracer
    s.RestoreEvents

    for i in tr1:
        break
    assert len(s[i.ROOT]) == len(tr1)

    for i in tr2:
        break
    assert len(s[i.ROOT]) == len(tr2)

    for i in tr1:
        assert s[i.hash]
    for i in tr2:
        assert s[i.hash]

    trsum = tr1 + tr2
    for i in s:
        assert trsum[i.hash]

    del s
    del trsum

    for i in tr1:
        assert i.hash
    for i in tr2:
        assert i.hash

    try:
        for i in tr2:
            i.cross_section
        for i in tr2:
            assert i.cross_section
    except AttributeError:
        pass

    del tr1
    del tr2

    # Check for memory leaks
    for i in range(10):
        s = SampleTracer()
        s.OutputDirectory = "Project"
        s.EventCache = True
        s.RestoreTracer
        s.RestoreEvents

        k = sum([s for l in range(1000)])
        del s

    try:
        shutil.rmtree("Project")
        shutil.rmtree("tmp")
    except:
        pass


if __name__ == "__main__":
    test_tracer_addEvent()
    test_tracer_operators()
    test_tracer_hdf5()
    pass
