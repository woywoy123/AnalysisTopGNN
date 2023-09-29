from AnalysisG.Templates import EventTemplate
from examples.ParticlesOther import TopChildren, Jet

class EventOther(EventTemplate):

    def __init__(self):
        EventTemplate.__init__(self)


        # ========= Event Variable Declaration ========= #
        self.weight = "weight_mc"
        self.mu = "mu"
        self.met = "met_met"
        self.phi = "met_phi"

        self.Objects = {
                "jets" : Jet(),
                "children" : TopChildren(),
        }
        # ============================================== #
        self.Trees = ["nominal"]

    def CompileEvent(self):
        self.jets = list(self.jets.values())
        self.children = list(self.children.values())
        self.all_particles = self.jets + self.children
