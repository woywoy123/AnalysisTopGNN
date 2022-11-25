from AnalysisTopGNN.Templates import EventTemplate
from AnalysisTopGNN.Particles.Particles import *

class Event(EventTemplate):

    def __init__(self):
        EventTemplate.__init__(self)
        self.Objects = {
                "Tops" : Top(), 
                "TopChildren" : Children(),
                "TruthJets" : TruthJet(), 
                "TruthJetPartons" : TruthJetPartons(),
                "Jets" : Jets(),
                "JetPartons" : JetPartons(),
                "Electrons" : Electron(), 
                "Muons" : Muon(),
        }
       
        self.Trees = ["nominal"]

        self.Lumi = "weight_mc"
        self.mu = "mu"

        self.DefineObjects()
        
        self._Deprecated = False
        self._CommitHash = "master@e633cf7b9b51de362222bd3175bfec8e6c00026f"

    def CompileEvent(self):
        self.JetPartons = { i : self.JetPartons[i] for i in self.JetPartons if self.JetPartons[i].index != []}
        self.TruthJetPartons = { i : self.TruthJetPartons[i] for i in self.TruthJetPartons if self.TruthJetPartons[i].index != []}

        # ---- Remove Null children ---- #
        for i in self.TopChildren:
            if isinstance(self.TopChildren[i].eta, float):
                continue
            self.TopChildren[i] = None
        self.TopChildren = { i : self.TopChildren[i] for i in self.TopChildren if self.TopChildren[i] != None }

        for i in self.TopChildren:
            t = self.TopChildren[i]
            if isinstance(t.index, list):
                continue
            self.Tops[t.index].Children.append(t)

        for jp in self.TruthJetPartons:
            tjp = self.TruthJetPartons[jp]
            tjp.TruthJet.append(self.TruthJets[tjp.TruJetIndex])
            self.TruthJets[tjp.TruJetIndex].Partons.append(tjp)

        for jp in self.JetPartons:
            tjp = self.JetPartons[jp]
            tjp.Jet.append(self.Jets[tjp.JetIndex])
            self.Jets[tjp.JetIndex].Partons.append(tjp)

        for i in self.TruthJets:
            for ti in self.TruthJets[i].index:
                if ti == -1:
                    continue
                self.Tops[ti].TruthJets.append(self.TruthJets[i])

        for i in self.Jets:
            for ti in self.Jets[i].index:
                if ti == -1:
                    continue
                self.Tops[ti].Jets.append(self.Jets[i])
   
        maps = {}
        for i in self.TopChildren:
            if abs(self.TopChildren[i].pdgid) not in [11, 13, 15]:
                continue
            maps[i] = self.TopChildren[i]
        
        # ==== Electron ==== #
        if len(self.Electrons) != 0:
            dist = {}
            for i in maps:
                for l in self.Electrons:
                    dist[maps[i].DeltaR(self.Electrons[l])] = [i, l]
            
            dst = sorted(dist) 
            for i in range(len(self.Electrons)):
                self.TopChildren[dist[dst[i]][0]].Children.append(self.Electrons[dist[dst[i]][1]])
                self.Electrons[dist[dst[i]][1]].Parent.append(self.TopChildren[dist[dst[i]][0]])
    
        # ==== Muon ==== #
        if len(self.Muons) != 0:
            dist = {}
            for i in maps:
                for l in self.Muons:
                    dist[maps[i].DeltaR(self.Muons[l])] = [i, l]
            
            dst = sorted(dist) 
            for i in range(len(self.Muons)):
                self.TopChildren[dist[dst[i]][0]].Children.append(self.Muons[dist[dst[i]][1]])
                self.Muons[dist[dst[i]][1]].Parent.append(self.TopChildren[dist[dst[i]][0]])
 
        self.Tops = list(self.Tops.values())
        self.TopChildren = list(self.TopChildren.values())
        self.Jets = list(self.Jets.values())
        self.TruthJets = list(self.TruthJets.values())
        self.Electrons = list(self.Electrons.values())
        self.Muons = list(self.Muons.values())

        self.DetectorObjects = self.Jets + self.Electrons + self.Muons
