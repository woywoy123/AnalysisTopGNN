from .EventIndexParticle import *
from AnalysisTopGNN.Templates import EventTemplate


class EventIndex(EventTemplate):
    def __init__(self):
        EventTemplate.__init__(self)
        self.Objects = {
            "Tops": Top(),
            "TopChildren": Children(),
            "TruthJets": TruthJet(),
            "TruthJetPartons": TruthJetPartons(),
            "Jets": Jets(),
            "JetPartons": JetPartons(),
            "Electrons": Electron(),
            "Muons": Muon(),
        }

        self.Trees = ["nominal"]

        self.Lumi = "weight_mc"
        self.mu = "mu"
        self.met = "met_met"
        self.met_phi = "met_phi"

        self.DefineObjects()

        self._Deprecated = True
        self._CommitHash = "master@e633cf7b9b51de362222bd3175bfec8e6c00026f"

    def CompileEvent(self):
        self.JetPartons = {
            i: self.JetPartons[i]
            for i in self.JetPartons
            if self.JetPartons[i].index != []
        }
        self.TruthJetPartons = {
            i: self.TruthJetPartons[i]
            for i in self.TruthJetPartons
            if self.TruthJetPartons[i].index != []
        }
        self.Tops = {t.index: t for t in self.Tops.values()}

        c = {}
        for i in self.TopChildren:
            if isinstance(self.TopChildren[i].eta, float):
                c[i] = self.TopChildren[i]
                continue
        self.TopChildren = {
            i: tc for i, tc in zip(range(len(c)), c.values()) if tc != None
        }

        for i in self.TopChildren:
            t = self.TopChildren[i]
            self.Tops[t.index].Children.append(t)
            t.Parent.append(self.Tops[t.index])
            t.FromRes = self.Tops[t.index].FromRes

        for i in self.TruthJets:
            for ti in self.TruthJets[i].index:
                if ti == -1:
                    continue
                self.Tops[ti].TruthJets.append(self.TruthJets[i])
                self.TruthJets[i].Tops.append(self.Tops[ti])

        for jp in self.TruthJetPartons:
            tjp = self.TruthJetPartons[jp]
            tjp.TruthJet.append(self.TruthJets[tjp.TruJetIndex])
            self.TruthJets[tjp.TruJetIndex].Partons.append(tjp)
            tjp.Parent.append(self.TopChildren[tjp.index])

        for i in self.Jets:
            for ti in self.Jets[i].index:
                if ti == -1:
                    continue
                self.Tops[ti].Jets.append(self.Jets[i])
                self.Jets[i].Tops.append(self.Tops[ti])

        for jp in self.JetPartons:
            tjp = self.JetPartons[jp]
            tjp.Jet.append(self.Jets[tjp.JetIndex])
            self.Jets[tjp.JetIndex].Partons.append(tjp)
            tjp.Parent.append(self.TopChildren[tjp.index])

        maps = {
            i: self.TopChildren[i]
            for i in self.TopChildren
            if abs(self.TopChildren[i].pdgid) in [11, 13, 15]
        }
        # ==== Electron ==== #
        if len(self.Electrons) != 0 and len(maps) != 0:
            dist = {
                maps[i].DeltaR(self.Electrons[l]): [i, l]
                for i in maps
                for l in self.Electrons
            }
            dst = sorted(dist)
            for i in range(len(self.Electrons)):
                self.TopChildren[dist[dst[i]][0]].Children.append(
                    self.Electrons[dist[dst[i]][1]]
                )
                self.Electrons[dist[dst[i]][1]].Parent.append(
                    self.TopChildren[dist[dst[i]][0]]
                )
                self.Electrons[dist[dst[i]][1]].index += list(
                    set([p.index for p in self.TopChildren[dist[dst[i]][0]].Parent])
                )

        # ==== Muon ==== #
        if len(self.Muons) != 0 and len(maps) != 0:
            dist = {
                maps[i].DeltaR(self.Muons[l]): [i, l] for i in maps for l in self.Muons
            }
            dst = sorted(dist)
            for i in range(len(self.Muons)):
                self.TopChildren[dist[dst[i]][0]].Children.append(
                    self.Muons[dist[dst[i]][1]]
                )
                self.Muons[dist[dst[i]][1]].Parent.append(
                    self.TopChildren[dist[dst[i]][0]]
                )
                self.Muons[dist[dst[i]][1]].index += list(
                    set([p.index for p in self.TopChildren[dist[dst[i]][0]].Parent])
                )

        self.Tops = list(self.Tops.values())
        self.TopChildren = list(self.TopChildren.values())
        self.Jets = list(self.Jets.values())
        self.TruthJetPartons = list(self.TruthJetPartons.values())
        self.TruthJets = list(self.TruthJets.values())
        self.Electrons = list(self.Electrons.values())
        self.Muons = list(self.Muons.values())

        self.DetectorObjects = self.Jets + self.Electrons + self.Muons
