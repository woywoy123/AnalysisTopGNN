from AnalysisTopGNN import Analysis
from AnalysisTopGNN.Events import Event 
from copy import copy 
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F
from AnalysisTopGNN.Tools import Threading 

Ana = Analysis()
Ana.InputSample("m2") #, "/CERN/Samples/SamplesLisa/*")
Ana.Event = Event 
Ana.EventCache = True 
Ana.DumpPickle = True
Ana.Launch()

def function(events):
    leptonic = [11, 12, 13, 14]
    accept = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    res = []
    
    it = -1
    for i in events:
        event = i.Trees["nominal"]
        top = event.Tops
        if len(top) != 4:
            continue
        it += 1 
        _Res = []
        stringR = {"Lep" : [], "Had" : []}
        for t in top:
            if len(t.TruthJets) == 0:
                continue

            if len([k.pdgid for k in t.Children if abs(k.pdgid) not in accept]) > 0:
                continue
            
            lp = "Lep" if sum([1 for k in t.Children if abs(k.pdgid) in leptonic]) > 0 else "Had"
            if lp == "Lep" and len(t.TruthJets) != 1:
                continue
        
            if lp == "Hep" and len(t.TruthJets) != 3:
                continue
            
            if lp == "Lep":
                t.TruthJets += [k for k in t.Children if abs(k.pdgid) in leptonic]
        
            stringR[lp].append(sum(t.TruthJets).CalculateMass())
            if t.FromRes == 1:
                _Res.append(t)
        
        if len(_Res) != 2:
            events[it] = []
            continue

        events[it] = [[sum(_Res).CalculateMass()], stringR] 
    return events


events = []
for i in Ana:
    events.append(i)

stringR = {"Lep" : [], "Had" : []}
res = []
TH = Threading(events, function, 5, 10)
TH.Start()
for i in TH._lists:
    if len(i) == 0:
        continue
    res += i[0]
    stringR["Lep"] += i[1]["Lep"]
    stringR["Had"] += i[1]["Had"]

### Criteria for being considered a top:
# -> If top decays hadronically, require 3 truth jets 
# -> If top decays leptonically, require 1 truth jet + lepton and neutrino (children based)

Plot = {
            "Title" : "Reconstructed Top Invariant Mass",
            "xMax" : 300, 
            "xMin" : 100,
            "xBins" : 200,
            "xTitle" : "Mass (GeV)", 
            "Style" : "ATLAS",
            "Filename" : "Tops",
        }
plt1 = copy(Plot)
plt1["xData"] = stringR["Had"]
plt1["Title"] = "Hadronic"

plt2 = copy(Plot)
plt2["xData"] = stringR["Lep"]
plt2["Title"] = "Leptonic"

x1 = TH1F(**plt1)
x2 = TH1F(**plt2)

pltx = copy(Plot)
pltx["Histograms"] = [x1, x2] 
x = CombineTH1F(**pltx)
x.SaveFigure()

pltR = copy(Plot)
pltR["xData"] = res
pltR["Filename"] = "Resonance"
pltR["Title"] = "Reconstructioned Resonance from Selection Tops"
pltR["xMax"] = 1500
pltR["xMin"] = 0
pltR["xBins"] = 200
x = TH1F(**pltR)
x.SaveFigure()

for i in stringR:
    print(i + " -> " + str(len(stringR[i])))
print(len(res))

