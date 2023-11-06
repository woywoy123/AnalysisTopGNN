from AnalysisG.Templates import GraphTemplate


class GraphTops(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        self.Particles = self.Event.Tops


class GraphChildren(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        self.Particles = self.Event.TopChildren


class GraphChildrenNoNu(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        self.Particles = [i for i in self.Event.TopChildren if not i.is_nu]


class GraphTruthJet(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        particles = self.Event.TruthJets
        particles += [i for i in self.Event.TopChildren if i.is_nu or i.is_lep]
        self.Particles = particles


class GraphTruthJetNoNu(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        particles = self.Event.TruthJets
        particles += [i for i in self.Event.TopChildren if i.is_lep]
        self.Particles = particles


class GraphJet(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        particles = self.Event.Jets
        particles += [i for i in self.Event.TopChildren if i.is_nu or i.is_lep]
        self.Particles = particles


class GraphJetNoNu(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        particles = self.Event.Jets
        particles += [i for i in self.Event.TopChildren if i.is_lep]
        self.Particles = particles


class GraphDetector(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        self.Particles = self.Event.DetectorObjects
