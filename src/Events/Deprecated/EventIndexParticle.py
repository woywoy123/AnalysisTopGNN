from AnalysisTopGNN.Templates import ParticleTemplate


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
        self.index = self.Type + "_index"
        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"
        self.FromRes = self.Type + "_FromRes"
        self.TruthJets = []
        self.Jets = []


class Children(Particle):
    def __init__(self):
        self.Type = "children"
        Particle.__init__(self)
        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"
        self.index = self.Type + "_TopIndex"
        self.TruthJetPartons = []
        self.JetPartons = []
        self.FromRes = 0


class TruthJet(Particle):
    def __init__(self):
        self.Type = "truthjet"
        Particle.__init__(self)
        self.index = self.Type + "_TopIndex"
        self.TruthJetPartons = []
        self.Tops = []


class TruthJetPartons(Particle):
    def __init__(self):
        self.Type = "truJparton"
        Particle.__init__(self)
        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"
        self.index = self.Type + "_ChildIndex"
        self.TruthJetIndex = self.Type + "_TruJetIndex"
        self.TruthJet = []
        self.Tops = []


class Electron(Particle):
    def __init__(self):
        self.Type = "el"
        Particle.__init__(self)
        self.charge = self.Type + "_charge"
        self.index = []


class Muon(Particle):
    def __init__(self):
        self.Type = "mu"
        Particle.__init__(self)
        self.charge = self.Type + "_charge"
        self.index = []


class Jets(Particle):
    def __init__(self):
        self.Type = "jet"
        Particle.__init__(self)
        self.index = self.Type + "_TopIndex"
        self.JetPartons = []
        self.Tops = []


class JetPartons(Particle):
    def __init__(self):
        self.Type = "Jparton"
        Particle.__init__(self)
        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"
        self.index = self.Type + "_ChildIndex"
        self.JetIndex = self.Type + "_JetIndex"
        self.Jet = []
