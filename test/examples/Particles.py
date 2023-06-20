from AnalysisG.Templates import ParticleTemplate


class Jet(ParticleTemplate):
    def __init__(self):
        ParticleTemplate.__init__(self)

        self.pt = "jet_pt"
        self.eta = "jet_eta"
        self.phi = "jet_phi"
        self.e = "jet_e"
        self.MatchedTops = "jet_TopIndex"


class LazyDefinition(ParticleTemplate):
    def __init__(self):
        ParticleTemplate.__init__(self)

        self.pt = self.Type + "_pt"
        self.eta = self.Type + "_eta"
        self.phi = self.Type + "_phi"
        self.e = self.Type + "_e"


class Top(LazyDefinition):
    def __init__(self):
        self.Type = "top"
        LazyDefinition.__init__(self)
        self.FromResonance = self.Type + "_FromRes"


class TopChildren(LazyDefinition):
    def __init__(self):
        self.Type = "children"
        LazyDefinition.__init__(self)
        self.index = self.Type + "_index"

