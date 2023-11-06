from AnalysisG.Templates import ParticleTemplate
from AnalysisG.Templates import EventTemplate
from AnalysisG.IO import PickleObject, UnpickleObject, UpROOT
from AnalysisG.Tools import Threading
from time import sleep
import psutil
import pickle

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
        for i in self.TruthJets: x.append(self.TruthJets[i])
        self.somethingelse = sum(x)
        self.p2 = self.somethingelse.Mass != 0


def test_particle_pickle():
    root1 = "./samples/sample1/smpl1.root"
    x = TruthJet()
    vals = x.__getleaves__()
    io = UpROOT(root1)
    io.Trees = ["nominal"]
    io.Leaves = list(vals.values())

    mem = 0
    for i in io:
        jet = x.clone()
        inpt = {}
        for k in i:
            g = k.split("/")
            if g[-1] not in io.Leaves: continue
            inpt[g[-1]] = i[k]
        jet.__build__(inpt)
        jets = jet.Children

        PickleObject(jets, "jets")
        jets_r = UnpickleObject("jets")
        assert sum([l == p for l, p in zip(jets, jets_r)]) == len(jets)
        if mem == 0: mem = psutil.virtual_memory().percent
        assert psutil.virtual_memory().percent - mem < 8


def test_particle_multithreading():
    def Functions(inpt, _prgbar):
        lock, bar = _prgbar
        out = []
        for i in inpt:
            j_, d_ = i
            j_ = j_.clone()
            x = j_.__build__(d_)
            out.append(x)
            if lock is None: continue
            with lock: bar.update(1)
        return out

    root1 = "./samples/sample1/smpl1.root"
    j = TruthJet()
    vals = j.__getleaves__()
    io = UpROOT(root1)
    io.Trees = ["nominal"]
    io.Leaves = list(vals.values())

    excl = ["MetaData", "ROOT", "EventIndex"]
    vals = {i : j for j, i in vals.items()}
    jets = []
    for i in io:
        jet = j.clone()
        jet.__build__({vals[k.split("/")[-1]] : i[k] for k in i if k not in excl})
        jets += jet.Children
        assert jets[-1].px != 0
        assert jets[-1].pt != 0

    mem = 0
    for _ in range(3):
        x = []
        for i in io:
            _dct = {vals[k.split("/")[-1]]: i[k] for k in i if k not in excl}
            x.append([j.clone(), _dct])
        th = Threading(x, Functions, 10, 2500)
        th.Start()
        x = []
        for i in th._lists: x += list(i.values())
        x = set(x)
        x = {i.hash: i for i in x}
        assert len(x) == len(jets)
        assert len([x[i.hash] for i in jets]) == len(jets)
        for i in list(x): del x[i]
        if mem == 0: mem = psutil.virtual_memory().percent
        assert mem - psutil.virtual_memory().percent < 8


def test_event_pickle():
    root1 = "./samples/sample1/smpl1.root"
    ev = Event()
    ev.__getleaves__()
    io = UpROOT(root1)
    io.Trees = ["nominal"]
    io.Leaves = ev.Leaves

    mem = 0
    for _ in range(3):
        events = []
        for i in io:
            event = ev.clone()
            events += event.__compiler__(i)

        PickleObject(events, "events")
        events_r = UnpickleObject("events")
        assert sum([l.hash == p.hash for l, p in zip(events, events_r)]) == len(events)

        if mem == 0: mem = psutil.virtual_memory().percent
        assert psutil.virtual_memory().percent - mem < 8



def test_event_multithreading():
    def Function(inpt, _prgbar = (None, None)):
        lock, bar = _prgbar
        out = []
        evnt = pickle.loads(inpt[0][0]).clone()
        for i in range(len(inpt)):
            _, val = inpt[i]
            _out = evnt.__compiler__(val)
            _out[-1].CompileEvent()
            inpt[i] = pickle.dumps(_out[-1])
            val = None
            _out = None
            if lock is None: continue
            with lock: bar.update(1)
        del evnt
        return inpt

    root1 = "./samples/sample1/smpl1.root"
    ev = Event()
    ev.__getleaves__()
    io = UpROOT(root1)
    io.Trees = ["nominal"]
    io.Leaves = ev.Leaves
    #import tracemalloc
    #tracemalloc.start()
    mem = 0
    for _ in range(3):
        events = []
        threads = []
        for i in io:
            _events = ev.__compiler__(i)
            _events[-1].CompileEvent()
            events += _events
            assert _events[-1].hash == pickle.loads(Function([ [ pickle.dumps(ev), i ] ])[0]).hash
            for _ in range(100): threads += [[pickle.dumps(ev), i]]

        th = Threading(threads, Function, 10, 200)
        th.Start()
        threads = None
        #snapshot = tracemalloc.take_snapshot()
        #print(snapshot.statistics("lineno"))
        events_j = []
        for i in th._lists: events_j.append(pickle.loads(i))
        events_j = list(set(events_j))

        assert len(events_j) == len(events)
        events_j = {i.index: i for i in events_j}
        events_i = {i.index: i for i in events}
        for i in events_j: assert events_j[i].hash == events_i[i].hash

        for i in events_j:
            m_j = events_j[i].something.Mass
            m_i = events_i[i].something.Mass
            assert m_i - m_j == 0
        for i in list(events_j): del events_j[i]

        if mem == 0: mem = psutil.virtual_memory().percent
        assert psutil.virtual_memory().percent - mem < 8


if __name__ == "__main__":
    test_particle_pickle()
    test_particle_multithreading()
    test_event_pickle()
    test_event_multithreading()
