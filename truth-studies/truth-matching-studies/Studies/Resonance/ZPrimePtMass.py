from AnalysisG.Templates import SelectionTemplate

class ZPrimeMatrix(SelectionTemplate):

    def __init__(self):
        SelectionTemplate.__init__(self)

        self.ZMatrixTops = {"Mass" : [], "PT" : []}

        self.ZMatrixChildren = {"Mass" : [], "PT" : []}
        self.ZMatrixChildren_DecayChain = {"HL" : 0, "HH" : 0, "LH" : 0, "LL" : 0}

        self.ZMatrixTJ = {"Mass" : [], "PT" : []}
        self.ZMatrixTJ_NTJ = {"NumTJ" : [], "NumTops" : []}

        self.ZMatrixJ = {"Mass" : [], "PT" : []}
        self.ZMatrixJ_NJ = {"NumJ" : [], "NumTops" : []}

    def Selection(self, event):
        # Check if the events have only two resonance tops
        tops = [t for t in event.Tops if t.FromRes == 1]
        if len(tops) > 2: return False

    def Strategy(self, event):

        lep = [ 11, 12, 13, 14, 15, 16]

        tops = [t for t in event.Tops if t.FromRes]
        ZP = sum(tops)
        self.ZMatrixTops["Mass"].append(ZP.Mass/1000)
        self.ZMatrixTops["PT"].append(ZP.pt/1000)

        decay = {"HL" : [], "HH" : [], "LL" : [], "LH" : []}

        t1, t2 = tops
        dec = ("L" if t1.LeptonicDecay else "H") + ("L" if t2.LeptonicDecay else "H")
        decay[dec] += t1.Children + t2.Children
        leps = [i for i in decay[dec] if abs(i.pdgid) in lep] if "L" in dec else []
        self.ZMatrixChildren_DecayChain[dec] += 1

        ZC = sum(decay[dec])
        self.ZMatrixChildren["Mass"].append(ZC.Mass/1000)
        self.ZMatrixChildren["PT"].append(ZC.pt/1000)

        uniqTJ = t1.TruthJets + t2.TruthJets
        tj = {hex(id(i)) : i for i in uniqTJ}
        self.ZMatrixTJ_NTJ["NumTJ"] += [len(tj)]
        self.ZMatrixTJ_NTJ["NumTops"] += [len({hex(id(j)) : 0 for i in uniqTJ for j in i.Tops})]

        tj = sum(list(tj.values()) + leps)
        self.ZMatrixTJ["Mass"] += [tj.Mass/1000]
        self.ZMatrixTJ["PT"] += [tj.pt/1000]

        uniqJ = t1.Jets + t2.Jets
        jets = {hex(id(i)) : i for i in uniqJ}
        self.ZMatrixJ_NJ["NumJ"] += [len(jets)]
        self.ZMatrixJ_NJ["NumTops"] += [len({hex(id(j)) : 0 for i in uniqJ for j in i.Tops})]

        jets = sum(list(jets.values()) + leps)
        self.ZMatrixJ["Mass"] += [jets.Mass/1000]
        self.ZMatrixJ["PT"] += [jets.pt/1000]
