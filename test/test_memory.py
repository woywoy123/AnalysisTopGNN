from AnalysisG.Templates import ParticleTemplate
from AnalysisG.Templates import EventTemplate
from AnalysisG.IO import PickleObject, UnpickleObject, UpROOT
from AnalysisG.Tools import Threading
from time import sleep
import psutil
from conftest import clean_dir


class Particle(ParticleTemplate):
    def __init__(self):
        ParticleTemplate.__init__(self)
        self.pt = self.Type + "_pt"
        self.eta = self.Type + "_eta"
        self.phi = self.Type + "_phi"
        self.e = self.Type + "_e"


class TruthJetParton(Particle):
    def __init__(self):
        self.Type = "TJparton"
        Particle.__init__(self)

        self.index = self.Type + "_index"
        self.TruthJetIndex = self.Type + "_TruthJetIndex"
        self.TopChildIndex = self.Type + "_ChildIndex"
        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"


class TruthJet(Particle):
    def __init__(self):
        self.Type = "truthjets"
        Particle.__init__(self)
        self.is_btagged = self.Type + "_btagged"

    @property
    def is_b(self):
        return self.is_btagged


class Event(EventTemplate):
    def __init__(self):
        EventTemplate.__init__(self)
        self.index = "eventNumber"
        self.weight = "weight_mc"
        self.Trees = ["nominal"]
        self.met_phi = "met_phi"
        self.CommitHash = "..."
        self.Deprecated = False
        self.Objects = {"Partons": TruthJetParton(), "TruthJets": TruthJet()}

    def CompileEvent(self):
        x = []
        for i in self.Partons:
            x.append(self.Partons[i])
        self.something = sum(x)
        self.p1 = self.something.Mass != 0

        x = []
        for i in self.TruthJets:
            x.append(self.TruthJets[i])
        self.somethingelse = sum(x)
        self.p2 = self.somethingelse.Mass != 0


def test_particle_pickle():
    root1 = "./samples/sample1/smpl1.root"
    x = TruthJet()
    vals = x.__interpret__
    io = UpROOT(root1)
    io.Trees = ["nominal"]
    io.Leaves = list(vals.values())

    mem = 0
    for i in io:
        jet = x.clone
        jet.__interpret__ = {
            k.split("/")[-1]: i[k] for k in i if k.split("/")[-1] in io.Leaves
        }
        jets = jet.Children

        PickleObject(jets, "jets")
        jets_r = UnpickleObject("jets")

        assert sum([l == p for l, p in zip(jets, jets_r)]) == len(jets)

        if mem == 0:
            mem = psutil.virtual_memory().percent
        assert psutil.virtual_memory().percent - mem < 0.5

    clean_dir()


def test_particle_multithreading():
    root1 = "./samples/sample1/smpl1.root"
    j = TruthJet()
    vals = j.__interpret__
    io = UpROOT(root1)
    io.Trees = ["nominal"]
    io.Leaves = list(vals.values())

    jets = []
    for i in io:
        jet = j.clone
        jet.__interpret__ = {
            k.split("/")[-1]: i[k] for k in i if k.split("/")[-1] in io.Leaves
        }
        jets += jet.Children

    mem = 0
    for _ in range(3):
        x = []
        for i in io:
            for t in range(1000):
                x.append(
                    [
                        j,
                        {
                            k.split("/")[-1]: i[k]
                            for k in i
                            if k.split("/")[-1] in io.Leaves
                        },
                    ]
                )

        def Function(inpt, _prgbar):
            lock, bar = _prgbar
            out = []
            for i in inpt:
                t, val = i
                p = t.clone
                p.__interpret__ = val
                out.append(p.Children)
                with lock:
                    bar.update(1)
                del p
                del t
                del val
            return out

        th = Threading(x, Function, 4, 2500)
        th.Start
        x = []
        for i in th._lists:
            x += i

        x = set(x)
        assert len(x) == len(jets)
        x = {i.hash: i for i in x}
        try:
            assert len([x[i.hash] for i in jets]) == len(jets)
        except KeyError:
            raise AssertionError

        def Function(inpt, _prgbar):
            lock, bar = _prgbar
            for i in inpt:
                p = i.clone
                del p
                del i
            return []

        th = Threading([j for _ in range(10000)], Function, 5, 2000)
        th.Start

        if mem == 0:
            mem = psutil.virtual_memory().percent
        assert mem - psutil.virtual_memory().percent < 1


def test_event_pickle():
    root1 = "./samples/sample1/smpl1.root"
    ev = Event()
    ev.__interpret__
    io = UpROOT(root1)
    io.Trees = ["nominal"]
    io.Leaves = ev.Leaves

    mem = 0
    for _ in range(3):
        events = []
        for i in io:
            event = ev.clone
            events += event.__compiler__(i)
            events[-1].hash = root1

        PickleObject(events, "events")
        events_r = UnpickleObject("events")
        assert sum([l == p for l, p in zip(events, events_r)]) == len(events)

        if mem == 0:
            mem = psutil.virtual_memory().percent
        print(psutil.virtual_memory().percent - mem < 1)
        assert psutil.virtual_memory().percent - mem < 1

    clean_dir()


def test_event_multithreading():
    root1 = "./samples/sample1/smpl1.root"
    ev = Event()
    ev.__interpret__
    io = UpROOT(root1)
    io.Trees = ["nominal"]
    io.Leaves = ev.Leaves

    mem = 0
    for _ in range(3):
        events = []
        for i in io:
            events += ev.__compiler__(i)
            events[-1].hash = root1
            events[-1].CompileEvent()

        def Function(inpt, _prgbar):
            lock, bar = _prgbar
            out = []
            for i in inpt:
                evnt, root, val = i
                out += evnt.__compiler__(val)
                out[-1].hash = root
                out[-1].CompileEvent()
                with lock:
                    bar.update(1)
                del val
                del evnt
            return out

        th = Threading(
            [[ev.clone, root1, i] for i in io for _ in range(10)], Function, 10, 74
        )
        th.Start
        events_j = []
        for i in th._lists:
            events_j.append(i)
        events_j = list(set(events_j))
        assert len(events_j) == len(events)

        events_j = {i.hash: i for i in events_j}

        assert round(events_j[events[0].hash].something.Mass, 4) == round(
            events[0].something.Mass, 4
        )
        try:
            assert len([events_j[i.hash] for i in events]) == len(events)
        except KeyError:
            raise AssertionError

        if mem == 0:
            mem = psutil.virtual_memory().percent
        assert psutil.virtual_memory().percent - mem < 10


if __name__ == "__main__":
    # test_particle_pickle()
    # test_particle_multithreading()
    test_event_pickle()
    test_event_multithreading()
