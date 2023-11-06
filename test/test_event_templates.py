from AnalysisG.Templates import ParticleTemplate
from AnalysisG.Templates import EventTemplate
from AnalysisG.IO import UpROOT

def test_event_template():
    root1 = "./samples/sample1/smpl1.root"

    class Event(EventTemplate):
        def __init__(self):
            EventTemplate.__init__(self)
            self.index = "eventNumber"
            self.weight = "weight_mc"
            self.Trees = ["nominal"]
            self.met_phi = "met_phi"
            self.CommitHash = "..."
            self.Deprecated = False

    ev = Event()
    val = ev.__getleaves__()
    assert "eventNumber" in val["event"]["index"]
    assert "weight_mc" in val["event"]["weight"]
    assert "met_phi" in val["event"]["met_phi"]
    assert "CommitHash" not in val["event"]
    assert "Deprecated" not in val["event"]
    assert "Trees" not in val["event"]
    assert "Branches" not in val["event"]
    assert "Leaves" not in val["event"]
    assert "Objects" not in val["event"]

    ev.index = 0
    assert len(ev.hash) == 18

    ev2 = Event()
    ev2.index = 1
    assert ev2 != ev


def test_event_particle_template():
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
            self.Trees = ["nominal"]
            self.met_phi = "met_phi"
            self.CommitHash = "..."
            self.Deprecated = False

    ev = Event()
    vals = ev.__getleaves__()
    assert "eventNumber" == vals["event"]["index"]
    assert "weight_mc" == vals["event"]["weight"]
    assert "met_phi" == vals["event"]["met_phi"]

    assert "top_pt" == vals["top"]["pt"]
    assert "top_phi" == vals["top"]["phi"]
    assert "top_eta" == vals["top"]["eta"]
    assert "top_e" == vals["top"]["e"]

    assert "children_pt" == vals["Children"]["pt"]
    assert "children_phi" == vals["Children"]["phi"]
    assert "children_eta" == vals["Children"]["eta"]
    assert "children_e" == vals["Children"]["e"]
    x  = len(vals["event"])
    x += len(vals["Children"])
    x += len(vals["top"])
    assert x == 11

def test_event_particle_template_populate():
    root1 = "./samples/sample1/smpl1.root"

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
            self.Objects = {
                "top": Top(),
                "Children": Children,
            }
            self.index = "eventNumber"
            self.weight = "weight_mc"
            self.Trees = ["nominal", "truth"]
            self.met_phi = "met_phi"
            self.CommitHash = "..."
            self.Deprecated = False

    ev = Event()
    ev.__getleaves__()

    io = UpROOT(root1)
    io.Trees = ev.Trees
    io.Leaves = ev.Leaves
    meta = io.GetAmiMeta()

    lst, lstc, lstt = [], [], []
    all_ev = []
    n_children = 0
    n_tops = 0

    for i in io:
        Trees = ev.__compiler__(i)
        if "nominal/eventNumber" in i:
            assert len(Trees) == 2
            assert sum([sum([k.index >= 0, k.weight != 0]) for k in Trees]) == 4
            t1, t2 = Trees

            c = sum([len(k) for k in i["nominal/children_e"]])
            x = [float(k) for j in i["nominal/children_e"] for k in j]
            assert len(t1.Children) == c
            assert sum(x) == sum([t.e for t in t1.Children.values()])
            n_children += len(t1.Children)
            n_tops += len(t1.top)

            lst.append(t1)
            lstc += [t for t in t1.Children.values()]

            lstt += [t for t in t1.top.values()]
            assert len(t1.hash) == 18
            assert t1 != t2
        else: pass
        all_ev.append(i)

    n_events = len(lst)
    assert len(all_ev) == 1000
    assert n_events != 0
    assert n_children != 0
    assert n_tops != 0
    assert n_events == len(set(lst))
    assert n_children == len(set(lstc))
    assert n_tops == len(set(lstt))

if __name__ == "__main__":
    test_event_template()
    test_event_particle_template()
    test_event_particle_template_populate()

