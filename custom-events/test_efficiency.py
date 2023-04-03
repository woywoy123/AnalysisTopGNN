from ObjectDefinitions.Particles import Child, TruthJet, TruthJetParton
import json

def create_particle(pdgid, top_index, from_res): #px, py, pz, E, 
    p = Child()
    #p.px, p.py, p.pz, p.e, p.pdgid, p.TopIndex, p.FromRes = px, py, pz, E, pdgid, top_index, from_res
    p.pdgid, p.TopIndex, p.FromRes = pdgid, top_index, from_res

    return p 

class CustomEvent:

    def __init__(self, event_dict):
        self.children_dict = event_dict["children"]
        self.tops_fromRes = event_dict["tops_fromRes"]
        self.truthJets_dict = event_dict["truthJets"]
        self.group_assignment = event_dict["group_assignment"]
        self.fromRes_assignment = event_dict["fromRes_assignment"]
        self.Children = []
        self.Leptons = []
        self.TruthJets = []

    def create_children(self):

        for c in range(len(self.children_dict["pdgid"])):
            child = create_particle(self.children_dict["pdgid"][c], self.children_dict["topIndex"][c], self.tops_fromRes[self.children_dict["topIndex"][c]])
            self.Children.append(child)
            if abs(child.pdgid) in [11, 13, 15]:
                self.Leptons.append(child)

    def create_truthJets(self):

        for t in range(len(self.truthJets_dict["pdgid"])):
            tj = TruthJet()
            for p in range(len(self.truthJets_dict["pdgid"][t])):
                parton = TruthJetParton(self.truthJets_dict["pdgid"][t][p], self.truthJets_dict["topIndex"][t][p], self.truthJets_dict["topChildIndex"][t][p], self.tops_fromRes[self.truthJets_dict["topIndex"][t][p]])
                parton.Parent = self.Children[parton.TopChildIndex]
                tj.Parton.append(parton)
            self.TruthJets.append(tj)

    def create_groups(self):
        self.LeptonicGroup = {"res": [], "spec": []}
        self.HadronicGroup = {"res": [], "spec": []}

        for l, group in enumerate(self.group_assignment["leptons"]):
            origin = "res" if self.fromRes_assignment[group] else "spec"
            self.LeptonicGroup[origin].append(self.Leptons[l])
        for tj, group in enumerate(self.group_assignment["truthJets"]):
            origin = "res" if self.fromRes_assignment[group] else "spec"
            if group in self.group_assignment["leptons"]:
                self.LeptonicGroup[origin].append(self.TruthJets[tj])
            else:
                self.HadronicGroup[origin].append(self.TruthJets[tj])

def Efficiency(group, fromRes = False):
    print(f"In Efficiency with fromRes = {fromRes}")
    doesPass = False
    allPartonsProperty = {}
    if len(group) == 2:
        allPartonsProperty = { 0: [group[0].FromRes if fromRes else group[0].TopIndex], 1: [p.Parent.FromRes if fromRes else p.Parent.TopIndex for p in group[1].Parton] }
    else:
        allPartonsProperty = {i: [p.Parent.FromRes if fromRes else p.Parent.TopIndex for p in tj.Parton] for i,tj in enumerate(group)}
    print(f"allPartonsProperty = {allPartonsProperty}")
    intersectionProperty = set.intersection(*map(set,allPartonsProperty.values()))
    print(f"intersectionProperty: {intersectionProperty}")
    if not fromRes and intersectionProperty:
        doesPass = True 
    elif fromRes and intersectionProperty == {1}:
        doesPass = True 
    return doesPass

with open("Events.json") as f:
    jsondata = json.load(f)

for event in jsondata["events"]:

    if not event["to_run"]: continue

    ev = CustomEvent(event)
    ev.create_children()
    ev.create_truthJets()
    ev.create_groups()

    print(f"CHILDREN = {[c.pdgid for c in ev.Children]}\n")
    print(f"LEPTONS = {[l.pdgid for l in ev.Leptons]}")
    print(f"-> TopIndex = {[l.TopIndex for l in ev.Leptons]}")
    print(f"-> FromRes = {[l.FromRes for l in ev.Leptons]}\n")
    truthJets_pdgid = {i: [parton.pdgid for parton in tj.Parton] for i,tj in enumerate(ev.TruthJets)}
    truthJets_topIndex = {i: [parton.TopIndex for parton in tj.Parton] for i,tj in enumerate(ev.TruthJets)}
    truthJets_topChildIndex = {i: [parton.TopChildIndex for parton in tj.Parton] for i,tj in enumerate(ev.TruthJets)}
    truthJets_fromRes = {i: [parton.FromRes for parton in tj.Parton] for i,tj in enumerate(ev.TruthJets)}
    print(f"TRUTHJETs = {truthJets_pdgid}")
    print(f"-> TopIndex = {truthJets_topIndex}")
    print(f"-> TopChildIndex = {truthJets_topChildIndex}")
    print(f"-> FromRes = {truthJets_fromRes}\n")
    print(f"GROUPS = ")
    print(f"Leptonic group from spec = {[ev.LeptonicGroup['spec'][0].pdgid, [parton.pdgid for parton in ev.LeptonicGroup['spec'][1].Parton]]}")
    print(f"Leptonic group from res = {[ev.LeptonicGroup['res'][0].pdgid, [parton.pdgid for parton in ev.LeptonicGroup['res'][1].Parton]]}")
    hadGroupSpec_pdgid = [[parton.pdgid for parton in tj.Parton] for tj in ev.HadronicGroup['spec']]
    hadGroupRes_pdgid = [[parton.pdgid for parton in tj.Parton] for tj in ev.HadronicGroup['res']]
    print(f"Hadronic group from spec = {hadGroupSpec_pdgid}")
    print(f"Hadronic group from res = {hadGroupRes_pdgid}\n")
    print("EFFICIENCIES")
    print("-> Grouping:")
    print(f"Leptonic group from spec: {Efficiency(ev.LeptonicGroup['spec'])}")
    print(f"Leptonic group from res: {Efficiency(ev.LeptonicGroup['res'])}")
    print(f"Hadronic group from spec: {Efficiency(ev.HadronicGroup['spec'])}")
    print(f"Hadronic group from res: {Efficiency(ev.HadronicGroup['res'])}")
    print("-> Resonance assignment:")
    print(f"Leptonic group from spec: {Efficiency(ev.LeptonicGroup['spec'], True)}")
    print(f"Leptonic group from res: {Efficiency(ev.LeptonicGroup['res'], True)}")
    print(f"Hadronic group from spec: {Efficiency(ev.HadronicGroup['spec'], True)}")
    print(f"Hadronic group from res: {Efficiency(ev.HadronicGroup['res'], True)}")

