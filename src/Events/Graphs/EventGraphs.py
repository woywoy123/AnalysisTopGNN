from AnalysisG.Templates import GraphTemplate


class GraphTops(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += self.Event.Tops


class GraphChildren(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += self.Event.TopChildren


class GraphChildrenNoNu(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += [i for i in self.Event.TopChildren if not i.is_nu]


class GraphTruthJet(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += self.Event.TruthJets
        self.Particles += [i for i in self.Event.TopChildren if i.is_nu or i.is_lep]


class GraphTruthJetNoNu(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += self.Event.TruthJets
        self.Particles += [i for i in self.Event.TopChildren if i.is_lep]


class GraphJet(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += self.Event.Jets
        self.Particles += [i for i in self.Event.TopChildren if i.is_nu or i.is_lep]


class GraphJetNoNu(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += self.Event.Jets
        self.Particles += [i for i in self.Event.TopChildren if i.is_lep]


class GraphDetector(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += self.Event.DetectorObjects
