from AnalysisG.Particles.Particles import Electron, Muon, Children, TruthJet, Jet

def Efficiency_weighted1(group, top_assignment, event):
    if not group: 
        return 0
    #print(f"-->In Efficiency_weighted1 with top_assignment {top_assignment}")
    efficiency_objects = []
    for obj in group:
        #print(f"-> New object of type {type(obj)}")
        if isinstance(obj, Electron) or isinstance(obj, Muon):
            #print("Object is reco lepton")
            dR_dict = {c: obj.DeltaR(c) for c in event.Children if c.is_lep}
            #print(f"dR_dict = {dR_dict}")
            closest = {l:dR for l,dR in dR_dict.items() if dR == min(dR_dict.values())}
            #print(f"closest = {closest}")
            if not closest:
                #print("Could not find closest truth lepton")
                efficiency_objects.append(0.)
                continue
            closestL = closest.keys()[0]
            #print(f"TopIndex of closest truth lepton is {closestL.TopIndex}")
            efficiency_objects.append(1. if closestL.TopIndex == top_assignment else 0.)
            #print(f"Appending {1. if closestL.TopIndex == top_assignment else 0.} to efficiency_objects")
        elif isinstance(obj, Children):
            #print("Object is truth child")
            #print(f"TopIndex of child is {obj.TopIndex}")
            efficiency_objects.append(1. if obj.TopIndex == top_assignment else 0.)
            #print(f"Appending {1. if obj.TopIndex == top_assignment else 0.} to efficiency_objects")
        elif isinstance(obj, TruthJet) or isinstance(obj, Jet):
            #print("Object is jet or truth jet")
            #print("Parton eneries and topIndex")
            #for p in obj.Parton:
                #print(f"E = {p.e}, TopIndex = {[p.Parent[i].TopIndex for i in range(len(p.Parent))]}")
            #print(f"Appending {sum([p.e*(p.Parent[0].TopIndex == top_assignment) for p in obj.Parton])/sum([p.e for p in obj.Parton]) if obj.Parton else 0.} to efficiency_object")
            efficiency_objects.append(sum([p.e*(p.Parent[0].TopIndex == top_assignment) for p in obj.Parton])/sum([p.e for p in obj.Parton])) if obj.Parton else 0.
    efficiency_group = sum(efficiency_objects)/len(efficiency_objects) if efficiency_objects else 0.
    #print(f"efficiency_group = {efficiency_group}")
    return efficiency_group

def Efficiency_weighted2(group, top_assignment, event):
    if not group:
        return 0
    #print(f"-->In Efficiency_weighted2 with top_assignment {top_assignment}")
    efficiency_objects = []
    weights = []
    for obj in group:
        #print(f"-> New object of type {type(obj)}")
        if isinstance(obj, Electron) or isinstance(obj, Muon):
            #print("Object is reco lepton")
            dR_dict = {c: obj.DeltaR(c) for c in event.Children if c.is_lep}
            #print(f"dR_dict = {dR_dict}")
            closest = {l:dR for l,dR in dR_dict.items() if dR == min(dR_dict.values())}
            #print(f"closest = {closest}")
            if not closest:
                #print("Could not find closest truth lepton")
                efficiency_objects.append(0.)
                continue
            closestL = closest.keys()[0]
            #print(f"TopIndex of closest truth lepton is {closestL.TopIndex}")
            #print(f"Appending {obj.e if closestL.TopIndex == top_assignment else 0.} to efficiency_objects")
            efficiency_objects.append(obj.e if closestL.TopIndex == top_assignment else 0.)
            weights.append(obj.e)
        elif isinstance(obj, Children):
            #print("Object is truth child")
            #print(f"TopIndex of child is {obj.TopIndex}")
            #print(f"Appending {obj.e if obj.TopIndex == top_assignment else 0.} to efficiency_objects")
            efficiency_objects.append(obj.e if obj.TopIndex == top_assignment else 0.)
            weights.append(obj.e)
        elif isinstance(obj, TruthJet) or isinstance(obj, Jet):
            #print("Object is jet or truth jet")
            #print("Parton eneries and topIndex")
            #for p in obj.Parton:
                #print(f"E = {p.e}, TopIndex = {[p.Parent[i].TopIndex for i in range(len(p.Parent))]}")
            for p in obj.Parton:
                #print(f"Appending {p.e*(p.Parent[0].TopIndex == top_assignment)} to efficiency_objects")
                efficiency_objects.append(p.e*(p.Parent[0].TopIndex == top_assignment))
                weights.append(p.e)
    efficiency_group = sum(efficiency_objects)/(sum(weights)) if weights else 0.
    #print(f"efficiency_group = {efficiency_group}")
    return efficiency_group



