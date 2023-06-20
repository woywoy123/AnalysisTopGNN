from .ExperimentalParticles import *
from AnalysisTopGNN.Templates import EventTemplate


class ExperimentalEvent(EventTemplate):
    def __init__(self):
        EventTemplate.__init__(self)

        self.Tree = ["nominal"]
        self.Objects = {
            "Electrons": Electron(),
            "Muons": Muon(),
            "Tops": Top(),
            "TopChildren": TopChild(),
            "TruthJets": TruthJet(),
            "TruthJetChildren": TruthJetChild(),
            "Jets": Jet(),
        }

        self.runNumber = "runNumber"
        self.ee = "ee"
        self.mumu = "mumu"
        self.emu = "emu"

        self.DefineObjects()

    def CompileEvent(self, ClearVal=True):
        def RecursiveMass(inp):
            inp.SelfMass()
            inp.MassFromChild()
            for p in inp.Daughter:
                RecursiveMass(p)

        collect = {}
        for i in self.TopChildren:
            t = self.TopChildren[i][0]
            if t.topindex not in collect:
                collect[t.topindex] = {}
            if t.index not in collect[t.topindex]:
                collect[t.topindex][t.index] = []
            collect[t.topindex][t.index].append(t)

            if t.index > 0:
                collect[t.topindex][t.index - 1][-1].Daughter.append(t)

        self.Tops = []
        for i in collect:
            self.Tops.append(collect[i][0][0])
            RecursiveMass(self.Tops[i])

        self.TopChildren = self.DictToList(self.TopChildren)
