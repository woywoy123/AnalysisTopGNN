from AnalysisG.Events.Events.ssml.Particles import *
from AnalysisG.Templates import EventTemplate

class SSML(EventTemplate):
    def __init__(self):
        EventTemplate.__init__(self)
        self.Objects = {
            "Electrons": Electron(),
            "Jets": Jet(),
            "Muons": Muon(),
        }

        self.Trees = ["nominal_Loose"]

        self.index = "eventNumber"
        self.is_mc = "mcChannelNumber"
        self.met = "met_met"
        self.phi = "met_phi"

        self.weight = "weight_mc"
        self.mu = "mu"

    def CompileEvent(self):

        self.Jets = list(self.Jets.values())
        self.Electrons = list(self.Electrons.values())
        self.Muons = list(self.Muons.values())
        self.Detector = self.Jets + self.Electrons + self.Muons


