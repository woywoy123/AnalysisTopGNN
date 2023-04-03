from AnalysisTopGNN.Templates import Selection 

class ResonanceMassFromChildren(Selection):

    def __init__(self):
        Selection.__init__(self)
        self.ResonanceMass = {"Had-Had" : [], "Had-Lep" : [], "Lep-Lep" : []}
    
    def Selection(self, event):
        if len(event.Tops) != 4:
            return False
        return len([t for t in event.Tops if t.FromRes == 1]) == 2

    def Strategy(self, event):
        _leptons = [11, 12, 13, 14, 15, 16]
        stringTC = {"Had" : [], "Lep" : []}
        for t in event.Tops:
            if t.FromRes == 0:
                continue
            lp = "Lep" if sum([1 for c in t.Children if abs(c.pdgid) in _leptons]) > 0 else "Had"
            stringTC[lp] += t.Children
        
        modes = list(stringTC)
        modes.sort()
        self.ResonanceMass["-".join(modes)].append(sum([ i for j in stringTC.values() for i in j ]).Mass)


