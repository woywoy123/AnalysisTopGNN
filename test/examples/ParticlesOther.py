from AnalysisG.Templates import ParticleTemplate

class Particle(ParticleTemplate):

    def __init__(self):
        ParticleTemplate.__init__(self)

        self.eta = self.Type + "_eta"
        self.pt = self.Type + "_pt"
        self.phi = self.Type + "_phi"
        self.e = self.Type + "_e"


class TopChildren(Particle):

    def __init__(self):
        self.Type = "children"
        Particle.__init__(self)

class Jet(Particle):

    def __init__(self):
        self.Type = "jet"
        Particle.__init__(self)
