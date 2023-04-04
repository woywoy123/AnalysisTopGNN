from ObjectDefinitions.Particles import *
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
                "DecayParticles" : DecayParticles()
        }
       
        self.Trees = ["nominal"]

        self.Lumi = "weight_mc"
        self.runNumber = "runNumber"
        self.mu = "mu"
        self.met = "met_met"
        self.met_phi = "met_phi"

        self.DefineObjects()
        
        self._Deprecated = False
        self._CommitHash = "master@8be38e6e52aac66d761ce14f5666dcc392fce907"

    def CompileEvent(self):
        self.Tops = {t.index : t for t in self.Tops.values()}
        self.TopChildren = {c.index : c for c in self.TopChildren.values() if isinstance(c.index, int)}
        self.TruthJets = {tj.index : tj for tj in self.TruthJets.values()}
        self.TruthJetPartons = {tj.index : tj for tj in self.TruthJetPartons.values()}
        self.Jets = {j.index : j for j in self.Jets.values()}
        self.JetPartons = {j.index : j for j in self.JetPartons.values()}

        for c in self.TopChildren.values():
            self.Tops[c.TopIndex].Children.append(c)
            c.Parent.append(self.Tops[c.TopIndex])
            c.index = c.TopIndex
        
        for tj in self.TruthJets.values():
            for ti in tj.TopIndex:
                if ti == -1:
                    continue
                tj.Tops.append(self.Tops[ti])
                self.Tops[ti].TruthJets.append(tj)
            tj.index = tj.TopIndex
        
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
            j.index = j.TopIndex

        for jp in self.JetPartons.values():
            self.Jets[jp.JetIndex].Parton.append(jp)
            jp.Children.append(self.Jets[jp.JetIndex])
            for ci in jp.TopChildIndex:
                jp.Parent.append(self.TopChildren[ci])

        maps = { i : self.TopChildren[i] for i in self.TopChildren if abs(self.TopChildren[i].pdgid) in [11, 13, 15] }
        lep = list(self.Electrons.values()) + list(self.Muons.values())
        dist = { maps[i].DeltaR(j) : (i, j) for i in maps for j in lep }
        dst = sorted(dist)
        accept = []
        for dr in dst:
            idx, l = dist[dr]
            if l in accept:
                continue
            maps[idx].Children.append(l)
            l.index = [maps[idx].index]
            accept.append(l)
        
        self.Tops = list(self.Tops.values())
        self.Tops.reverse()
        self.TopChildren = list(self.TopChildren.values())
        self.TopChildren.reverse()
        self.TruthJets = list(self.TruthJets.values())
        self.Jets = list(self.Jets.values())
        self.Electrons = list(self.Electrons.values())
        self.Muons = list(self.Muons.values())

        self.DetectorObjects = self.Jets + self.Electrons + self.Muons

        collect = {}
        for i in self.DecayParticles.values():
            if i.TopIndex not in collect:
                collect[i.TopIndex] = {}
            if i.index not in collect[i.TopIndex]:
                collect[i.TopIndex][i.index] = []
            collect[i.TopIndex][i.index].append(i)
            
            if i.index-1 not in collect[i.TopIndex]:
                continue
            if i.index > 0:
                collect[i.TopIndex][i.index-1][-1].Children.append(i)
                i.Parent.append(collect[i.TopIndex][i.index-1][-1])
        
        for i in collect:
            x_m = min(list(collect[i]))
            self.Tops[i].DecayChildren += collect[i][x_m]
            for c in collect[i][x_m]:
                c.Parent.append(self.Tops[i])
