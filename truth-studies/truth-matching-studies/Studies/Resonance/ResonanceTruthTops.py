from AnalysisG.Templates import SelectionTemplate

class ResonanceDecayModes(SelectionTemplate):

    def __init__(self):
        SelectionTemplate.__init__(self)
        self.ResDecayMode = {"H" : 0, "L": 0, "HH" : 0, "HL" : 0, "LL" : 0}
        self.TopDecayMode = {"Spec-H" : 0, "Spec-L" : 0, "Res-H" : 0, "Res-L" : 0}

    def Selection(self, event):
        if len(event.Tops) != 4:
            return False
        return len([t for t in event.Tops if t.FromRes == 1]) == 2

    def Strategy(self, event):
        resT = [t for t in event.Tops if t.FromRes == 1]
        specT = [t for t in event.Tops if t.FromRes == 0]
        
        t1, t2 = resT
        r_dec1, r_dec2 = "L" if t1.LeptonicDecay else "H", "L" if t2.LeptonicDecay else "H"
        self.TopDecayMode["Res-" + r_dec1] += 1 
        self.TopDecayMode["Res-" + r_dec2] += 1
        self.ResDecayMode[r_dec1] += 1
        self.ResDecayMode[r_dec2] += 1

        t1, t2 = specT       
        s_dec1, s_dec2 = "L" if t1.LeptonicDecay else "H", "L" if t2.LeptonicDecay else "H"
        self.TopDecayMode["Spec-" + s_dec1] += 1 
        self.TopDecayMode["Spec-" + s_dec2] += 1 

        r_dec = r_dec1 + r_dec2
        r_dec = "HL" if r_dec == "LH" else r_dec 
        self.ResDecayMode[r_dec]+=1

class ResonanceMassFromTops(SelectionTemplate):

    def __init__(self):
        SelectionTemplate.__init__(self)
        self.ResDecayMode = {"HH" : [], "HL" : [], "LL" : []}
    
    def Selection(self, event):
        return len([t for t in event.Tops if t.FromRes == 1]) == 2

    def Strategy(self, event):
        resT = [t for t in event.Tops if t.FromRes == 1]
      
        t1, t2 = resT
        dec = ("L" if t1.LeptonicDecay else "H") + ("L" if t2.LeptonicDecay else "H")
        dec = "HL" if dec == "LH" else dec 
        self.ResDecayMode[dec] += [sum(resT).Mass/1000]

class ResonanceDeltaRTops(SelectionTemplate):
    
    def __init__(self):
        SelectionTemplate.__init__(self)
        self.TopsTypes = {"Res-Spec" : [], "Res-Res" : [], "Spec-Spec" : []}

    def Selection(self, event):
        if len(event.Tops) != 4:
            return False
        return sum([i.FromRes for i in event.Tops]) == 2
    
    def Strategy(self, event):
        fin = []
        for t1 in event.Tops:
            for t2 in event.Tops:
                if t1 == t2 or t2 in fin:
                    continue
                string = {"Res" : 0, "Spec" : 0}           
                string["Res" if t1.FromRes == 1 else "Spec"] += 1
                string["Res" if t2.FromRes == 1 else "Spec"] += 1
                self.TopsTypes["-".join([k for k in string for p in range(string[k])])].append(t1.DeltaR(t2))
            fin.append(t1)

class ResonanceTopKinematics(SelectionTemplate):

    def __init__(self):
        SelectionTemplate.__init__(self)
        self.TopsTypesPT = {"Res" : [], "Spec" : []}
        self.TopsTypesE = {"Res" : [], "Spec" : []}
        self.TopsTypesEta = {"Res" : [], "Spec" : []}
        self.TopsTypesPhi = {"Res" : [], "Spec" : []}

    def Selection(self, event):
        if len(event.Tops) != 4:
            return False
        return sum([i.FromRes for i in event.Tops]) == 2

    def Strategy(self, event):
        for t in event.Tops:
            self.TopsTypesPT["Res" if t.FromRes == 1 else "Spec"] += [t.pt / 1000]
            self.TopsTypesE["Res" if t.FromRes == 1 else "Spec"] += [t.e / 1000]
            self.TopsTypesEta["Res" if t.FromRes == 1 else "Spec"] += [t.eta]
            self.TopsTypesPhi["Res" if t.FromRes == 1 else "Spec"] += [t.phi]

