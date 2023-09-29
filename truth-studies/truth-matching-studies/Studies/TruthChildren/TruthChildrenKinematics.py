from AnalysisG.Templates import SelectionTemplate

class DeltaRChildren(SelectionTemplate):
    
    def __init__(self):
        SelectionTemplate.__init__(self)
        self.ChildrenCluster = {
                        "Had-DelR" : [], "Lep-DelR" : [],
                        "Had-top-PT" : [], "Lep-top-PT" : [], 
                        "Res-DelR" : [], "Spec-DelR" : [], 
        }
        self.TopChildrenCluster = {"Had" : [], "Lep" : []}
        self.MatchedChildren = {
                        "Correct-Top-Res-Res" : [], "False-Top-Res-Res" : [],
                        "Correct-Top-Spec-Spec" : [], "False-Top-Res-Spec" : [], 
                        "False-Top-Spec-Spec" : []
        }


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
                    if c2 == c or c2 in com: continue
                    self.ChildrenCluster[lp + "-DelR"] += [c2.DeltaR(c)]
                    self.ChildrenCluster[res + "-DelR"] += [c2.DeltaR(c)]
                    self.ChildrenCluster[lp + "-top-PT"] += [t.pt/1000]
                com.append(c)
            self.TopChildrenCluster[lp] += [t.DeltaR(c) for c in t.Children]          
        
        children = [c for t in event.Tops for c in t.Children]
        com = []
        for c1 in children:
            dic = {} 
            for c2 in children:
                if c1 == c2: continue
                dic[c1.DeltaR(c2)] = [c1.Parent[0] == c2.Parent[0], c1.FromRes + c2.FromRes]
            l = list(dic)
            l.sort()
            case = dic[l[0]] 
            if case[0] == True and case[1] == 2:
                self.MatchedChildren["Correct-Top-Res-Res"] += [l[0]]
            elif case[0] == False and case[1] == 2:
                self.MatchedChildren["False-Top-Res-Res"] += [l[0]]
            elif case[0] == False and case[1] == 1:
                self.MatchedChildren["False-Top-Res-Spec"] += [l[0]]
            elif case[0] == True and case[1] == 0:
                self.MatchedChildren["Correct-Top-Spec-Spec"] += [l[0]]
            elif case[0] == False and case[1] == 0:
                self.MatchedChildren["False-Top-Spec-Spec"] += [l[0]]


class TruthChildrenKinematics(SelectionTemplate):
    
    def __init__(self):
        SelectionTemplate.__init__(self)
        self.FractionalPT = {}
        self.FractionalEnergy = {}

    def Selection(self, event):
        if len(event.Tops) != 4:
            return False
        return len([t for t in event.Tops if t.FromRes == 1]) == 2
    
    def Strategy(self, event):
        for t in event.Tops:
            for c in t.Children:
                if c.symbol not in self.FractionalPT:
                    self.FractionalPT[c.symbol] = []
                if c.symbol not in self.FractionalEnergy:
                    self.FractionalEnergy[c.symbol] = []
                self.FractionalPT[c.symbol] += [c.pt/t.pt]
                self.FractionalEnergy[c.symbol] += [c.e/t.e]
