from AnalysisTopGNN.Templates import EventTemplate
from ObjectDefinitions.Particles import Children, TruthJet, TruthJetParton

class Event(EventTemplate):

    def __init__(self):
        EventTemplate.__init__(self)
        
        # ===== Event Variable Declaration ===== # 

        self.Trees = ["nominal"]

        self.Objects = {
                "Children" : Children(),
                "TruthJets": TruthJet(),
                "TruthJetPartons": TruthJetParton(),

                }
        # ===== End of declaration ===== #
        self.DefineObjects()
    
    def CompileEvent(self): 

        children = {"pdgid": [5, -11, 12, -5, -14, 13, 5, 2, -1, -5, -4, 3], "topIndex": [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]}
        tops_fromRes = [0, 1, 1, 0]
        truthJets = {"pdgid": [[5], [-5], [5], [2], [-1], [-5], [-4], [3]], "topIndex": [[0], [1], [2], [2], [2], [3], [3], [3]]}

        self.Children = []
        self.Leptons = []
        for c in range(len(children["pdgid"])):
            child = Children(children["pdgid"][c], children["topIndex"][c], tops_fromRes[children["topIndex"][c]])
            self.Children.append(child)
            if child.is_lep:
                self.Leptons.append(child)

        self.TruthJets = []
        for t in range(len(truthJets["pdgid"])):
            tj = TruthJet()
            for p in range(len(truthJets["pdgid"][t])):
                parton = TruthJetParton(truthJets["pdgid"][t][p], truthJets["topIndex"][t][p], tops_fromRes[truthJets["topIndex"][t][p]])
                tj.Parton.append(parton)
            self.TruthJets.append(tj)
        
        
