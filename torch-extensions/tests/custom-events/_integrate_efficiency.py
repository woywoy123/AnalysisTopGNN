from ObjectDefinitions.Particles import Child, TruthJet, TruthJetParton
import json
from statistics import mean

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
        # self.fromRes_assignment = event_dict["fromRes_assignment"]
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
            origin = "res" if self.tops_fromRes[group] else "spec"
            self.LeptonicGroup[origin].append(self.Leptons[l])
        for tj, group in enumerate(self.group_assignment["truthJets"]):
            origin = "res" if self.tops_fromRes[group] else "spec"
            if group in self.group_assignment["leptons"]:
                self.LeptonicGroup[origin].append(self.TruthJets[tj])
            else:
                self.HadronicGroup[origin].append(self.TruthJets[tj])

def Efficiency_weighted(group, top_assignment, method):
    if method not in [0,1]:
        print("Method for Efficiency not recognized. Must be either 0 or 1")
        return
    efficiency_objects = []
    weights = []
    for obj in group:
        # if isinstance(obj, Electron) or isinstance(obj, Muon) or isinstance(obj, Children):
        if isinstance(obj, Child):
            #truthObj = obj if isinstance(obj, Children) else obj.Parent
            truthObj = obj
            w = 1. if method == 0 else obj.e
            efficiency_objects.append(w*(truthObj.TopIndex == top_assignment))
            weights.append(obj.e)
        elif isinstance(obj, TruthJet): # or isinstance(obj, Jet):
            ws = []
            for p in obj.Parton:
                w = p.e*(p.Parent.TopIndex == top_assignment)
                if method == 1:
                    efficiency_objects.append(p.e*(p.Parent.TopIndex == top_assignment))
                    weights.append(p.e)
                else:
                    ws.append(w)
            if method == 0: 
                efficiency_objects.append(sum(ws)/sum([p.e for p in obj.Parton])) if obj.Parton else 0.
    denom = len(efficiency_objects) if method == 0 else sum(weights)
    efficiency_group = sum(efficiency_objects)/denom if denom else 0.
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

    res_flags = {'res': 1, 'spec': 0}
    topIndicesRes = {res_key: list(set([t for t in event["children"]["topIndex"] if event["tops_fromRes"][t] == res_value])) for res_key, res_value in res_flags.items()}
    children_topIndices = {res_key: {topIndex: [pdgid for c,pdgid in enumerate(event["children"]["pdgid"]) if event["children"]["topIndex"][c] == topIndex] for topIndex in topIndicesRes[res_key]} for res_key in res_flags.keys()}
    topIndices = {res_key: {'lep': [index for index, clist in children_topIndices[res_key].items() if any([abs(pdgid) in _leptons for pdgid in clist])][0], 'had': [index for index, clist in children_topIndices[res_key].items() if not any([abs(pdgid) in _leptons for pdgid in clist])][0]} for res_key in res_flags.keys()}
    print("EFFICIENCIES")
    for method in range(2):
        efficiencies = []
        print(f"-> Method {method+1}:")
        for decay in ['lep', 'had']:
            for origin in ['spec', 'res']:
                group = ev.LeptonicGroup[origin] if decay == 'lep' else ev.HadronicGroup[origin]
                eff_group = Efficiency_weighted(group, topIndices[origin][decay], method)
                efficiencies.append(eff_group)
                print(f"{'Leptonic' if decay == 'lep' else 'Hadronic'} from {origin}: {eff_group}")
        print(f"=> Event efficiency: {mean(efficiencies)}")

