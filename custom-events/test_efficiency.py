from ObjectDefinitions.Particles import Child, TruthJet, TruthJetParton
import json

_leptons = [11, 13, 15]

def create_particle(pdgid, top_index, from_res, energy): 
    p = Child(pdgid, top_index, from_res, energy)

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
            child = create_particle(self.children_dict["pdgid"][c], self.children_dict["topIndex"][c], self.tops_fromRes[self.children_dict["topIndex"][c]], self.children_dict["energy"][c])
            self.Children.append(child)
            if abs(child.pdgid) in _leptons:
                self.Leptons.append(child)

    def create_truthJets(self):

        for t in range(len(self.truthJets_dict["pdgid"])):
            tj = TruthJet()
            for p in range(len(self.truthJets_dict["pdgid"][t])):
                parton = TruthJetParton(self.truthJets_dict["pdgid"][t][p], self.truthJets_dict["topIndex"][t][p], self.truthJets_dict["topChildIndex"][t][p], self.tops_fromRes[self.truthJets_dict["topIndex"][t][p]], self.truthJets_dict["energy"][t][p])
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

def Efficiency_boolean1(group, fromRes = False):
    if len(group) == 2: had = False
    else: had = True
    #print(f"In Efficiency with fromRes = {fromRes}")
    doesPass = False
    allPartonsProperty = {}
    if not had:
        allPartonsProperty = { 0: [(group[0].FromRes if fromRes else group[0].TopIndex) if group[0].pdgid != 21 else None], 1: [(p.Parent.FromRes if fromRes else p.Parent.TopIndex) if p.pdgid != 21 else None for p in group[1].Parton] }
    else:
        allPartonsProperty = {i: [(p.Parent.FromRes if fromRes else p.Parent.TopIndex) if p.pdgid != 21 else None for p in tj.Parton] for i,tj in enumerate(group)}
    #print(f"allPartonsProperty = {allPartonsProperty}")
    intersectionProperty = set.intersection(*map(set,allPartonsProperty.values()))
    #print(f"intersectionProperty: {intersectionProperty}")
    if not fromRes and intersectionProperty:
        doesPass = True 
    elif fromRes and intersectionProperty == {1}:
        doesPass = True 
    return doesPass

def Efficiency_boolean2(group, fromRes = False):
    if len(group) == 2: had = False
    else: had = True
    #print(f"In Efficiency with fromRes = {fromRes}")
    doesPass = False
    allPartonsProperty = {}
    if not had:
        allPartonsProperty = { 0: [(group[0].FromRes if fromRes else group[0].TopIndex) if group[0].pdgid != 21 else None], 1: [(p.Parent.FromRes if fromRes else p.Parent.TopIndex) if p.pdgid != 21 else None for p in group[1].Parton] }
        allPartonsPDGID = { 0: [abs(group[0].pdgid)], 1: [abs(p.pdgid) for p in group[1].Parton] }
    else:
        allPartonsProperty = {i: [(p.Parent.FromRes if fromRes else p.Parent.TopIndex) if p.pdgid != 21 else None for p in tj.Parton] for i,tj in enumerate(group)}
        allPartonsPDGID = { i: [abs(p.pdgid) for p in tj.Parton] for i,tj in enumerate(group)}
    # print(f"allPartonsProperty = {allPartonsProperty}")
    # print(f"allPartonsPDGID = {allPartonsPDGID}")
    intersectionProperty = set.intersection(*map(set,allPartonsProperty.values()))
    # print(f"intersectionProperty: {intersectionProperty}")
    if not fromRes and intersectionProperty:
        for commonTop in intersectionProperty:
            commonTopChildrenPDGID = [allPartonsPDGID[i][j] for i in allPartonsPDGID.keys() for j in range(len(allPartonsPDGID[i])) if allPartonsProperty[i][j] == commonTop]
            if had:
                desiredPDGIDs = [i for i in range(6)]
                numDesired = 3
            else:
                desiredPDGIDs = [5, 11, 13, 15]
                numDesired = 2
            desiredTopChildrenPDGID = [i for i in commonTopChildrenPDGID if i in desiredPDGIDs]
            if len(desiredTopChildrenPDGID) >= numDesired and 5 in desiredTopChildrenPDGID:
                doesPass = True
    elif fromRes and intersectionProperty == {1}:
        doesPass = True 
    return doesPass

def Efficiency_boolean3(group, fromRes = False):
    if len(group) == 2: had = False
    else: had = True
    #print(f"In Efficiency with fromRes = {fromRes}")
    doesPass = False
    allPartonsProperty = {}
    if not had:
        allPartonsProperty = [(group[0].FromRes if fromRes else group[0].TopIndex) if group[0].pdgid != 21 else None] + [(p.Parent.FromRes if fromRes else p.Parent.TopIndex) if p.pdgid != 21 else None for p in group[1].Parton]
        allPartonsPDGID = [abs(group[0].pdgid)] + [abs(p.pdgid) for p in group[1].Parton]
    else:
        allPartonsProperty = [(p.Parent.FromRes if fromRes else p.Parent.TopIndex) if p.pdgid != 21 else None for i,tj in enumerate(group) for p in tj.Parton]
        allPartonsPDGID = [abs(p.pdgid) for i,tj in enumerate(group) for p in tj.Parton]
    #print(f"allPartonsProperty = {allPartonsProperty}")
    #print(f"allPartonsPDGID = {allPartonsPDGID}")
    sortedPartonsPDGID = {prop: [allPartonsPDGID[i] for i in range(len(allPartonsPDGID)) if allPartonsProperty[i] == prop] for prop in allPartonsProperty}
    #print(f"sortedPartonsPDGID = {sortedPartonsPDGID}")
    for prop, partonsFromTop in sortedPartonsPDGID.items():
        if had: 
            check_ids = [i for i in range(5)]
            check_num = 2
        else: 
            check_ids = _leptons
            check_num = 1
        if not fromRes:
            if len([i for i in partonsFromTop if i in check_ids]) >= check_num and 5 in partonsFromTop:
                doesPass = True
        else:
            if prop == 1 and len([i for i in partonsFromTop if i in check_ids]) >= check_num and 5 in partonsFromTop:
                doesPass = True
    return doesPass

def Efficiency_continuous1(group, top_assignment, had = True):
    if had: truthjets = group 
    else: truthjets = group[1:]
    efficiency_objects = [sum([1 for p in tj.Parton if p.Parent.TopIndex == top_assignment])/len(tj.Parton) for tj in truthjets]
    if not had: 
        efficiency_objects.append(1 if group[0].TopIndex == top_assignment else 0)
    # print(f"efficiency_objects = {efficiency_objects}")
    efficiency_group = sum(efficiency_objects)/len(group)
    # print(f"efficiency_group = {efficiency_group}")
    return efficiency_group

def Efficiency_continuous2(group, top_assignment, had = True):
    if had: truthjets = group 
    else: truthjets = group[1:]
    efficiency_objects = [p.Parent.TopIndex == top_assignment for tj in truthjets for p in tj.Parton]
    if not had: 
        efficiency_objects.append(group[0].TopIndex == top_assignment)
    # print(f"efficiency_objects = {efficiency_objects}")
    efficiency_group = sum(efficiency_objects)/len(efficiency_objects)
    # print(f"efficiency_group = {efficiency_group}")
    return efficiency_group

def Efficiency_weighted1(group, top_assignment, had = True):
    if had: truthjets = group 
    else: truthjets = group[1:]
    efficiency_objects = [sum([p.e*(p.Parent.TopIndex == top_assignment) for p in tj.Parton])/sum([p.e for p in tj.Parton]) for tj in truthjets]
    if not had: 
        efficiency_objects.append(1. if group[0].TopIndex == top_assignment else 0.)
    #print(f"efficiency_objects = {efficiency_objects}")
    efficiency_group = sum(efficiency_objects)/len(group)
    #print(f"efficiency_group = {efficiency_group}")
    return efficiency_group

def Efficiency_weighted2(group, top_assignment, had = True):
    if had: truthjets = group 
    else: truthjets = group[1:]
    efficiency_objects = [p.e*(p.Parent.TopIndex == top_assignment) for tj in truthjets for p in tj.Parton]
    if not had: 
        efficiency_objects.append(group[0].e * (group[0].TopIndex == top_assignment))
    #print(f"efficiency_objects = {efficiency_objects}")
    efficiency_group = sum(efficiency_objects)/(sum([p.e for tj in truthjets for p in tj.Parton]) + (group[0].e if not had else 0.))
    #print(f"efficiency_group = {efficiency_group}")
    return efficiency_group


with open("Events.json") as f:
    jsondata = json.load(f)

for i,event in enumerate(jsondata["events"]):

    if not event["to_run"]: continue

    print(f"------{i+1}------")
    print(f"Event: {event['name']}\n")

    ev = CustomEvent(event)
    ev.create_children()
    ev.create_truthJets()
    ev.create_groups()

    print(f"CHILDREN = {[c.pdgid for c in ev.Children]}\n")
    print(f"LEPTONS = {[l.pdgid for l in ev.Leptons]}")
    print(f"-> TopIndex = {[l.TopIndex for l in ev.Leptons]}")
    print(f"-> FromRes = {[l.FromRes for l in ev.Leptons]}")
    print(f"-> Energy = {[l.e for l in ev.Leptons]}\n")
    truthJets_pdgid = {i: [parton.pdgid for parton in tj.Parton] for i,tj in enumerate(ev.TruthJets)}
    truthJets_topIndex = {i: [parton.TopIndex for parton in tj.Parton] for i,tj in enumerate(ev.TruthJets)}
    truthJets_topChildIndex = {i: [parton.TopChildIndex for parton in tj.Parton] for i,tj in enumerate(ev.TruthJets)}
    truthJets_fromRes = {i: [parton.FromRes for parton in tj.Parton] for i,tj in enumerate(ev.TruthJets)}
    truthJets_energy = {i: [parton.e for parton in tj.Parton] for i,tj in enumerate(ev.TruthJets)}
    print(f"TRUTHJETs = {truthJets_pdgid}")
    print(f"-> TopIndex = {truthJets_topIndex}")
    print(f"-> TopChildIndex = {truthJets_topChildIndex}")
    print(f"-> FromRes = {truthJets_fromRes}")
    print(f"-> Energy = {truthJets_energy}\n")
    print(f"GROUPS = ")
    print(f"Leptonic group from spec = {[ev.LeptonicGroup['spec'][0].pdgid, [parton.pdgid for parton in ev.LeptonicGroup['spec'][1].Parton]]}")
    print(f"Leptonic group from res = {[ev.LeptonicGroup['res'][0].pdgid, [parton.pdgid for parton in ev.LeptonicGroup['res'][1].Parton]]}")
    hadGroupSpec_pdgid = [[parton.pdgid for parton in tj.Parton] for tj in ev.HadronicGroup['spec']]
    hadGroupRes_pdgid = [[parton.pdgid for parton in tj.Parton] for tj in ev.HadronicGroup['res']]
    print(f"Hadronic group from spec = {hadGroupSpec_pdgid}")
    print(f"Hadronic group from res = {hadGroupRes_pdgid}\n")
    # print("EFFICIENCIES")
    # print("-> Grouping:")
    # print(f"Leptonic group from spec: {Efficiency(ev.LeptonicGroup['spec'])}")
    # print(f"Leptonic group from res: {Efficiency(ev.LeptonicGroup['res'])}")
    # print(f"Hadronic group from spec: {Efficiency(ev.HadronicGroup['spec'])}")
    # print(f"Hadronic group from res: {Efficiency(ev.HadronicGroup['res'])}")
    # print("-> Resonance assignment:")
    # print(f"Leptonic group from spec: {Efficiency(ev.LeptonicGroup['spec'], True)}")
    # print(f"Leptonic group from res: {Efficiency(ev.LeptonicGroup['res'], True)}")
    # print(f"Hadronic group from spec: {Efficiency(ev.HadronicGroup['spec'], True)}")
    # print(f"Hadronic group from res: {Efficiency(ev.HadronicGroup['res'], True)}")

    ## Continuous efficiencies
    res_flags = {'res': 1, 'spec': 0}
    topIndicesRes = {res_key: list(set([t for t in event["children"]["topIndex"] if event["tops_fromRes"][t] == res_value])) for res_key, res_value in res_flags.items()}
    children_topIndices = {res_key: {topIndex: [pdgid for c,pdgid in enumerate(event["children"]["pdgid"]) if event["children"]["topIndex"][c] == topIndex] for topIndex in topIndicesRes[res_key]} for res_key in res_flags.keys()}
    topIndices = {res_key: {'lep': [index for index, clist in children_topIndices[res_key].items() if any([abs(pdgid) in _leptons for pdgid in clist])][0], 'had': [index for index, clist in children_topIndices[res_key].items() if not any([abs(pdgid) in _leptons for pdgid in clist])][0]} for res_key in res_flags.keys()}
    print("EFFICIENCIES")
    print("-> Weighted method 1:")
    print(f"Leptonic group from spec: {Efficiency_weighted1(ev.LeptonicGroup['spec'], topIndices['spec']['lep'], False)}")
    print(f"Leptonic group from res: {Efficiency_weighted1(ev.LeptonicGroup['res'], topIndices['res']['lep'], False)}")
    print(f"Hadronic group from spec: {Efficiency_weighted1(ev.HadronicGroup['spec'], topIndices['spec']['had'], True)}")
    print(f"Hadronic group from res: {Efficiency_weighted1(ev.HadronicGroup['res'], topIndices['res']['had'], True)}")
    print("-> Weighted method 2:")
    print(f"Leptonic group from spec: {Efficiency_weighted2(ev.LeptonicGroup['spec'], topIndices['spec']['lep'], False)}")
    print(f"Leptonic group from res: {Efficiency_weighted2(ev.LeptonicGroup['res'], topIndices['res']['lep'], False)}")
    print(f"Hadronic group from spec: {Efficiency_weighted2(ev.HadronicGroup['spec'], topIndices['spec']['had'], True)}")
    print(f"Hadronic group from res: {Efficiency_weighted2(ev.HadronicGroup['res'], topIndices['res']['had'], True)}\n")

