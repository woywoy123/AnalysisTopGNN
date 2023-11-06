from AnalysisG.Templates import SelectionTemplate

class TopDecayModes(SelectionTemplate):
    def __init__(self):
        SelectionTemplate.__init__(self)
        self.CounterPDGID = {}
        self.TopCounter = 0
        self.TopMassTC = {"Had" : [], "Lep" : []}

    def Selection(self, event):
        if len(event.Tops) != 4: return False
        for t in event.Tops:
            if len(t.Children) != 0: continue
            return False

    def Strategy(self, event):
        for t in event.Tops:
            self.TopCounter += 1
            for c in t.Children:
                if c.symbol not in self.CounterPDGID: self.CounterPDGID[c.symbol] = 0
                self.CounterPDGID[c.symbol] += 1
            _leptons = [11, 12, 13, 14, 15, 16]
            mode = "Lep" if sum([i for i in t.Children if abs(i.pdgid) in _leptons]) else "Had"
            self.TopMassTC[mode] += [ sum(t.Children).Mass / 1000 ]
