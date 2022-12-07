from AnalysisTopGNN.Particles.Particles import *
from AnalysisTopGNN.Templates import EventTemplate

class Event(EventTemplate):

    def __init__(self):
        EventTemplate.__init__(self)
        self.Objects = {
                "Tops" : Top(), 
                "TopChildren" : Children(),
                "TruthJets" : TruthJet(),
                "TruthJetPartons" : TruthJetParton(),
                "Jets" : Jet(), 
                "JetPartons" : JetParton(),
                "Electrons" : Electron(), 
                "Muons" : Muon(),
        }
       
        self.Trees = ["nominal"]

        self.Lumi = "weight_mc"
        self.mu = "mu"
        self.met = "met_met"
        self.met_phi = "met_phi"

        self.DefineObjects()
        
        self._Deprecated = False
        self._CommitHash = "master@7d70c412a65160d897d0253cbb42e5accf2c5bcf"

    def CompileEvent(self):
        self.Tops = {t.index : t for t in self.Tops.values()} 
        self.TopChildren = {c.index : c for c in self.TopChildren.values() if isinstance(c.index, int)}
        self.TruthJets = {tj.index : tj for tj in self.TruthJets.values()}
        self.TruthJetPartons = {tj.index : tj for tj in self.TruthJetPartons.values()}
        self.Jets = {j.index : j for j in self.Jets.values()}
        self.JetPartons = {j.index : j for j in self.JetPartons.values()}
        
        for c in self.TopChildren.values():
            self.Tops[c.TopIndex].Children.append(c)
        
        for tj in self.TruthJets.values():
            for ti in tj.TopIndex:
                if ti == -1:
                    continue
                tj.Tops.append(self.Tops[ti])
                self.Tops[ti].TruthJets.append(tj)
        
        for tjp in self.TruthJetPartons.values():
            self.TruthJets[tjp.TruthJetIndex].Parton.append(tjp)
            tjp.Children.append(self.TruthJets[tjp.TruthJetIndex])
            for ci in tjp.TopChildIndex:
                tjp.Parent.append(self.TopChildren[ci])
 
        for j in self.Jets.values():
            for ti in j.TopIndex:
                if ti == -1:
                    continue
                j.Tops.append(self.Tops[ti])
                self.Tops[ti].Jets.append(j)
        
        for jp in self.JetPartons.values():
            self.Jets[jp.JetIndex].Parton.append(jp)
            jp.Children.append(self.Jets[jp.JetIndex])
            for ci in jp.TopChildIndex:
                jp.Parent.append(self.TopChildren[ci])

        maps = { i : self.TopChildren[i] for i in self.TopChildren if abs(self.TopChildren[i].pdgid) in [11, 13, 15] }
        # ==== Electron ==== #
        if len(self.Electrons) != 0 and len(maps) != 0:
            dist = { maps[i].DeltaR(self.Electrons[l]) : [i, l] for i in maps for l in self.Electrons } 
            dst = sorted(dist) 
            for i in range(len(self.Electrons)):
                self.TopChildren[dist[dst[i]][0]].Children.append(self.Electrons[dist[dst[i]][1]])
                self.Electrons[dist[dst[i]][1]].Parent.append(self.TopChildren[dist[dst[i]][0]])
                self.Electrons[dist[dst[i]][1]].index += list(set([p.index for p in self.TopChildren[dist[dst[i]][0]].Parent]))
    
        # ==== Muon ==== #
        if len(self.Muons) != 0 and len(maps) != 0:
            dist = { maps[i].DeltaR(self.Muons[l]) : [i, l] for i in maps for l in self.Muons } 
            dst = sorted(dist) 
            for i in range(len(self.Muons)):
                self.TopChildren[dist[dst[i]][0]].Children.append(self.Muons[dist[dst[i]][1]])
                self.Muons[dist[dst[i]][1]].Parent.append(self.TopChildren[dist[dst[i]][0]])
                self.Muons[dist[dst[i]][1]].index += list(set([p.index for p in self.TopChildren[dist[dst[i]][0]].Parent]))


        self.Tops = list(self.Tops.values())
        self.TopChildren = list(self.TopChildren.values())
        self.TruthJets = list(self.TruthJets.values())
        self.Jets = list(self.Jets.values())
        self.Electrons = list(self.Electrons.values())
        self.Muons = list(self.Muons.values())

        self.DetectorObjects = self.Jets + self.Electrons + self.Muons
