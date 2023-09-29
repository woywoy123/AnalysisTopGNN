from AnalysisG.Templates import SelectionTemplate

class ResonanceMassJets(SelectionTemplate):

    def __init__(self):
        SelectionTemplate.__init__(self)
        self.ResMassJets = {
                "Had-Lep" : [], 
                "Lep-Lep" : [], 
                "Had-Had" : []
        }

        self.ResMassTruthJets = {
                "Had-Lep" : [], 
                "Lep-Lep" : [], 
                "Had-Had" : []
        }

        self.ResMassTops = {
                "Had-Lep" : [], 
                "Lep-Lep" : [], 
                "Had-Had" : []
        }

        self.ResMassNJets = {
                "Had-Lep" : [], 
                "Lep-Lep" : [], 
                "Had-Had" : []
        }

        self.ResMassNTops = {}

    def Selection(self, event):
        if len(event.Tops) != 4: return False
        if len([i.FromRes for i in event.Tops if i.FromRes == 1]) != 2: return False    
        return True 

    def Strategy(self, event):
    
        jetcontainer, leps = [], []
        tjets = []
        modes = []
        ntops = []
        for t in event.Tops:
            if t.FromRes == 0: continue
            modes.append("Lep" if t.LeptonicDecay else "Had") 
            jetcontainer += t.Jets
            ntops += [x for y in t.Jets for x in y.Tops]

            tjets += t.TruthJets
            if not t.LeptonicDecay: continue
            leps += [c for c in t.Children if c.is_nu or c.is_lep]      

        if len(jetcontainer + leps) == 0: return "ERROR -> No Particles"
 
        modes.sort()
        modes = "-".join(modes)
        res_j = sum(set(jetcontainer + leps))
        res_tj = sum(set(tjets + leps))
        res_t = sum(set([i for i in event.Tops if i.FromRes == 1]))
        ntops = ["Res" if t.FromRes == 1 else "Spec" for t in set(ntops)]
        ntops.sort()
        ntops = "-".join(ntops)        
 
        self.ResMassJets[modes].append(res_j.Mass/1000)
        self.ResMassTruthJets[modes].append(res_tj.Mass/1000)
        self.ResMassTops[modes].append(res_t.Mass/1000)
        self.ResMassNJets[modes].append(len(jetcontainer)) 

        if ntops == "Res-Res": modes = "*" + modes
        if ntops not in self.ResMassNTops: self.ResMassNTops["(" + modes + ") " + ntops] = []        
        self.ResMassNTops["(" + modes + ") " + ntops].append(res_j.Mass/1000)
