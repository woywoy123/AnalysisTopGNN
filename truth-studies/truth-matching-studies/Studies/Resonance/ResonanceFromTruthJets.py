from AnalysisG.Templates import SelectionTemplate

class ResonanceMassTruthJets(SelectionTemplate):
    
    def __init__(self):
        SelectionTemplate.__init__(self)

        self.ResMassTruthJets = {"Had-Lep": [], "Lep-Lep" : [], "Had-Had" : []}
        self.ResMassTops = {"Had-Lep": [], "Lep-Lep" : [], "Had-Had" : []}

        self.ResMassNTruthJets = {"Had-Lep": [], "Lep-Lep" : [], "Had-Had" : []}

    def Selection(self, event):
        # Criteria: 
        # - Two tops need to originate from resonance 
        # - Truth jets need to have no more than two top contributions, 
        # provided they both originate from resonance. Otherwise, the truth jet 
        # can only have one top contribution 
        if len([i.FromRes for i in event.Tops if i.FromRes == 1]) != 2: return False
        for i in event.Tops:
            if i.FromRes == 0: continue
            for tj in i.TruthJets:
                if len(tj.Tops) == 1: continue
                
                # No more than two top contributions 
                if len(tj.Tops) > 2: return False
                
                # If there are two top contributions to the truth jet, both tops need to originate from resonance 
                if len([t for t in tj.Tops if t.FromRes == 1]) != 2: return False
                                
        return True

    def Strategy(self, event):

        # Get the truth jets which are associated with the resonant tops.
        jetcontainer = []
        for tj in event.TruthJets:
            if len(tj.Tops) == 0: continue
            resT = [t for t in tj.Tops if t.FromRes == 1]
            if len(resT) == 0: continue
            jetcontainer += [tj]
 
        # Check if there are exactly two tops in the collected truth jets 
        tops = []
        for tj in jetcontainer: tops += tj.Tops
        tops = list(set(tops))
        if len(tops) != 2: return "Reject -> Invalid-Tops"
        
        # Check which decay mode the parent tops underwent to produce jets 
        t1, t2 = tops
        string = []
        string += ["Lep"] if t1.LeptonicDecay else ["Had"]
        string += ["Lep"] if t2.LeptonicDecay else ["Had"]
        string.sort()
        string = "-".join(string)

        # If any of the tops are leptonic, get the neutrino and the associated lepton from the children 
        leps = []
        if t1.LeptonicDecay: leps += [c for c in t1.Children if c.is_lep or c.is_nu]
        if t2.LeptonicDecay: leps += [c for c in t2.Children if c.is_lep or c.is_nu]

        # Sum the leptons and truth jets, and remove potential duplicates
        self.ResMassNTruthJets[string] += [len(set(jetcontainer))]
        
        jetcontainer += leps
        jetcontainer = list(set(jetcontainer))
        resMassTJ = sum(jetcontainer).Mass/1000
        resMassT = (t1 + t2).Mass/1000

        self.ResMassTruthJets[string] += [resMassTJ]
        self.ResMassTops[string] += [resMassT]

class ResonanceMassTruthJetsNoSelection(SelectionTemplate):
    
    def __init__(self):
        SelectionTemplate.__init__(self)

        # Resonance Mass from Truth Jets
        self.ResMassTruthJets = {"Had-Lep": [], "Lep-Lep" : [], "Had-Had" : []}
        self.ResMassNTruthJets = {"Had-Lep": [], "Lep-Lep" : [], "Had-Had" : []}

        # Resonance mass from Truth Tops (Select only the resonant ones)
        self.ResMassTops = {"Had-Lep": [], "Lep-Lep" : [], "Had-Had" : []}
        
        # Number of truth tops contributing to truth jets included in the resonance reconstruction
        # This is to check for top's merging based on decay topology 
        self.ResNTopContributions = {"Had-Lep": [], "Lep-Lep" : [], "Had-Had" : []}
        self.ResMassNTopContributions = {}


    def Selection(self, event):
        return len(event.Tops) == 4 and len([t for t in event.Tops if t.FromRes == 1]) == 2

    def Strategy(self, event):
        t1, t2 = [t for t in event.Tops if t.FromRes == 1]
        string = []
        string += ["Lep"] if t1.LeptonicDecay else ["Had"]
        string += ["Lep"] if t2.LeptonicDecay else ["Had"]
        string.sort()
        string = "-".join(string)
        self.ResMassTops[string] += [(t1+t2).Mass/1000]
         
        jetcontainer = []
        for t in event.Tops: jetcontainer += t.TruthJets if t.FromRes == 1 else []
        jetcontainer = list(set(jetcontainer))
   
        # Get the leptons for each of the tops contributing to the truth jets 
        tops = list(set([t for tj in jetcontainer for t in tj.Tops]))
        leps = list(set([l for t in tops for l in t.Children if l.is_nu or l.is_lep]))
        resMass = sum(leps + jetcontainer).Mass/1000
        self.ResMassTruthJets[string] += [resMass]
        self.ResNTopContributions[string] += [len(tops)]
        if len(tops) not in self.ResMassNTopContributions: self.ResMassNTopContributions[len(tops)] = []
        self.ResMassNTopContributions[len(tops)] += [resMass]
