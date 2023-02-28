from AnalysisTopGNN.Templates import EventGraphTemplate

class EventGraphTops(EventGraphTemplate):
    def __init__(self, Event = None):
        EventGraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += self.Event.Tops

class EventGraphChildren(EventGraphTemplate):
    def __init__(self, Event = None):
        EventGraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += self.Event.TopChildren

class EventGraphChildrenNoNu(EventGraphTemplate):
    def __init__(self, Event = None):
        EventGraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += [i for i in self.Event.TopChildren if abs(i.pdgid) not in [12, 14, 16]]

class EventGraphTruthJetLepton(EventGraphTemplate):
    def __init__(self, Event = None):
        EventGraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += self.Event.TruthJets
        self.Particles += self.Event.Electrons
        self.Particles += self.Event.Muons

class EventGraphDetector(EventGraphTemplate):
    def __init__(self, Event = None):
        EventGraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += self.Event.DetectorParticles


