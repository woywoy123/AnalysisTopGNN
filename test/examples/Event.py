from AnalysisG.Templates import EventTemplate
from .Particles import Jet, Top, TopChildren

class EventEx(EventTemplate):
    def __init__(self):
        EventTemplate.__init__(self)

        # ===== Event Variable Declaration ===== #
        self.weight = "weight_mc"
        self.mu = "mu"
        self.met = "met_met"
        self.phi = "met_phi"

        self.Trees = ["nominal"]

        self.Objects = {
            "SomeJets": Jet(),
            "Tops": Top(),
            "Children": TopChildren(),
        }
        # ===== End of declaration ===== #
        self.CommitHash = "<Some Hash For Bookkeeping>"

    def CompileEvent(self):
        # Create njets variable for the event
        self.nJets = len(self.SomeJets)

        # Do some particle truth matching
        for i in self.SomeJets:
            index = self.SomeJets[i].MatchedTops
            if index[0] == -1:
                continue
            for t in index:
                self.SomeJets[i].Parent.append(self.Tops[t])

        # (Optional) Convert the dictionary to particle list.
        self.SomeJets = list(self.SomeJets.values())
        self.Tops = list(self.Tops.values())
        self.Children = list(self.Children.values())
