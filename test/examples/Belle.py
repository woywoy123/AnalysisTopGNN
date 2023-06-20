from AnalysisG.Templates import EventTemplate
from AnalysisG.Templates import ParticleTemplate


class Particle(ParticleTemplate):
    def __init__(self):
        ParticleTemplate.__init__(self)
        self.Type = "MCParticles"
        self.px = self.Type + ".m_momentum_x"
        self.py = self.Type + ".m_momentum_y"
        self.pz = self.Type + ".m_momentum_z"
        self.e = self.Type + ".m_energy"


class EventBelle(EventTemplate):
    def __init__(self):
        EventTemplate.__init__(self)

        self.Trees = ["tree"]
        self.Branches = ["MCParticles"]

        self.Objects = {
            "particle": Particle(),
        }

    def CompileEvent(self):
        return
