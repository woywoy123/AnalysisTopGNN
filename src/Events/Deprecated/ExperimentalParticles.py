from AnalysisTopGNN.Templates import ParticleTemplate


class GenericParticle(ParticleTemplate):
    def __init__(self):
        ParticleTemplate.__init__(self)

        self.pt = self.Type + "_pt"
        self.eta = self.Type + "_eta"
        self.phi = self.Type + "_phi"
        self.e = self.Type + "_e"

        self.Daughter = []
        self.Parent = []

    def SelfMass(self):
        self.CalculateMass()

    def MassFromChild(self):
        self.CalculateMass(self.Daughter, "MassDaught")


class Top(GenericParticle):
    def __init__(self):
        self.Type = "top"

        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"
        self.index = self.Type + "_index"

        GenericParticle.__init__(self)


class TopChild(GenericParticle):
    def __init__(self):
        self.Type = "children"

        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"
        self.index = self.Type + "_index"
        self.topindex = self.Type + "_TopIndex"
        self.jetindex = self.Type + "_JetIndex"
        self.truthjetindex = self.Type + "_TruthJetIndex"

        GenericParticle.__init__(self)


class TruthJet(GenericParticle):
    def __init__(self):
        self.Type = "truthjet"

        self.topindex = self.Type + "_TopIndex"
        self.pdgid = self.Type + "_pdgid"

        GenericParticle.__init__(self)


class TruthJetChild(GenericParticle):
    def __init__(self):
        self.Type = "truthjetChildren"

        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"
        self.index = self.Type + "_index"

        GenericParticle.__init__(self)


class Electron(GenericParticle):
    def __init__(self):
        self.Type = "el"

        self.charge = self.Type + "_charge"

        GenericParticle.__init__(self)


class Muon(GenericParticle):
    def __init__(self):
        self.Type = "mu"

        self.charge = self.Type + "_charge"

        GenericParticle.__init__(self)


class Jet(GenericParticle):
    def __init__(self):
        self.Type = "jet"

        self.index = self.Type + "_TopIndex"

        GenericParticle.__init__(self)
