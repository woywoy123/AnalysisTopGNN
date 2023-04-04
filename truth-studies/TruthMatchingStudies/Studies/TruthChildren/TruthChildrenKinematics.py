from AnalysisTopGNN.Templates import Selection

class DeltaRChildren(Selection):
    
    def __init__(self):
        Selection.__init__(self)
        self.ChildrenCluster = {
                        "Had-DelR" : [], "Lep-DelR" : [],
                        "Had-top-PT" : [], "Lep-top-PT" : [], 
                        "Res-DelR" : [], "Spec-DelR" : [], 
        }
        self.TopChildrenCluster = {"Had" : [], "Lep" : []}

    def Selection(self, event):
        if len(event.Tops) != 4:
            return False
        return len([t for t in event.Tops if t.FromRes == 1]) == 2
    
    def Strategy(self, event):
        _leptons = [11, 12, 13, 14, 15, 16]
        for t in event.Tops:
            lp = "Lep" if sum([1 for c in t.Children if abs(c.pdgid) in _leptons]) > 0 else "Had"
            res = "Res" if t.FromRes == 1 else "Spec"
            com = []
            for c in t.Children:
                for c2 in t.Children:
                    if c2 == c or c2 in com:
                        continue
                    self.ChildrenCluster[lp + "-DelR"] += [c2.DeltaR(c)]
                    self.ChildrenCluster[res + "-DelR"] += [c2.DeltaR(c)]
                    self.ChildrenClusterPT[lp + "-top-PT"] += [t.pt/1000]
                com.append(c)
            self.TopChildrenCluster[lp] += [t.DeltaR(c) for c in t.Children]          


