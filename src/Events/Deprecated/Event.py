from .EventParticles import *
from AnalysisTopGNN.Templates import EventTemplate


class Event(EventTemplate):
    def __init__(self):
        EventTemplate.__init__(self)
        self.Objects = {
            "Electrons": Electron(),
            "Muons": Muon(),
            "Jets": Jet(),
            "TruthJets": TruthJet(),
            "TruthTops": TruthTop(),
            "TruthTopChildren": TruthTopChildren(),
            "TopPreFSR": TopPreFSR(),
            "TopPostFSR": TopPostFSR(),
            "TopPostFSRChildren": TopPostFSRChildren(),
        }
        self.Trees = ["nominal"]
        self.runNumber = "runNumber"
        self.eventNumber = "eventNumber"

        tag = "weight"
        self.pileup = tag + "_pileup"
        self.leptonSF = tag + "_leptonSF"
        self.globalLeptonTriggerSF = tag + "_globalLeptonTriggerSF"
        self.Lumi = tag + "_mc"

        self.bTagSF_DL1_85 = tag + "_bTagSF_DL1_85"
        self.bTagSF_DL1_77 = tag + "_bTagSF_DL1_77"
        self.bTagSF_DL1_70 = tag + "_bTagSF_DL1_70"
        self.bTagSF_DL1_60 = tag + "_bTagSF_DL1_60"

        self.bTagSF_DL1r_85 = tag + "_bTagSF_DL1r_85"
        self.bTagSF_DL1r_77 = tag + "_bTagSF_DL1r_77"
        self.bTagSF_DL1r_70 = tag + "_bTagSF_DL1r_70"
        self.bTagSF_DL1r_60 = tag + "_bTagSF_DL1r_60"

        self.jvt = tag + "_jvt"
        self.indiv_SF_EL_Reco = tag + "_indiv_SF_EL_Reco"
        self.indiv_SF_EL_ID = tag + "_indiv_SF_EL_ID"
        self.indiv_SF_EL_Isol = tag + "_indiv_SF_EL_Isol"

        self.indiv_SF_MU_ID = tag + "_indiv_SF_MU_ID"
        self.indiv_SF_MU_Isol = tag + "_indiv_SF_MU_Isol"

        self.mu = "mu"
        self.mu_actual = "mu_actual"

        self.met = "met_met"
        self.met_phi = "met_phi"

        self.DefineObjects()

        self._Deprecated = True
        self._CommitHash = "master@6fa4f934"

    def CompileEvent(self):
        def RecursiveSignal(DecayList, sig, index):
            for p_i in DecayList:
                setattr(p_i, "FromRes", sig)
                setattr(p_i, "Index", index)
                RecursiveSignal(p_i.Children, sig, index)

        for i in self.TruthTopChildren.values():
            self.TruthTops[i.Index].Children += [i]

        for i in self.TopPostFSRChildren.values():
            self.TopPostFSR[i.Index].Children += [i]

        for i in self.TopPostFSR:
            setattr(self.TopPostFSR[i], "TruthJets", [])
            setattr(self.TopPostFSR[i], "Leptons", [])

        for i in self.TruthJets:
            self.TruthJets[i].Index = -1
            self.TruthJets[i].FromRes = 0

        for i in self.TruthJets:
            for t in self.TruthJets[i].GhostTruthJetMap:
                if t == -1:
                    continue
                self.TopPostFSR[t].TruthJets += [self.TruthJets[i]]

        for i in self.Jets:
            for tj in self.Jets[i].JetMapGhost:
                if tj == -1:
                    continue
                self.TruthJets[tj].Children += [self.Jets[i]]
                self.Jets[i].Parent += [self.TruthJets[tj]]

        self.Electrons = self.DictToList(self.Electrons)
        self.Muons = self.DictToList(self.Muons)
        self.Jets = self.DictToList(self.Jets)

        self.Leptons = []
        self.Leptons += self.Electrons
        self.Leptons += self.Muons

        All = [
            i for i in self.TopPostFSRChildren.values() if abs(i.pdgid) in [11, 13, 15]
        ]
        for j in self.Leptons:
            dr = 99
            low = ""
            for i in All:
                d = i.DeltaR(j)
                if dr < d:
                    continue
                dr = d
                low = i
            if low == "":
                continue
            j.Index = low.Index
            setattr(j, "FromRes", 0)
            self.TopPostFSR[low.Index].Leptons.append(j)
            j.Parent += [self.TopPostFSR[low.Index]]

        self.DetectorParticles = []
        self.DetectorParticles += self.Electrons
        self.DetectorParticles += self.Muons
        self.DetectorParticles += self.Jets

        self.TruthJets = self.DictToList(self.TruthJets)
        self.TruthTops = self.DictToList(self.TruthTops)
        self.TruthTopChildren = self.DictToList(self.TruthTopChildren)

        self.TopPreFSR = self.DictToList(self.TopPreFSR)
        self.TopPostFSR = self.DictToList(self.TopPostFSR)
        self.TopPostFSRChildren = self.DictToList(self.TopPostFSRChildren)

        for i in self.TopPostFSR:
            RecursiveSignal(i.Children, i.FromRes, i.Index)
            RecursiveSignal(i.TruthJets, i.FromRes, i.Index)
            RecursiveSignal(i.Leptons, i.FromRes, i.Index)
