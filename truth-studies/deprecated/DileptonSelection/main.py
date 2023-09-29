from AnalysisTopGNN import Analysis 
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.Plotting import TH1F


Ana = Analysis()
Ana.InputSample("m2", "/CERN/Samples/SamplesLisa/m2/") #Samples/Dilepton/Collections/ttH_tttt_m1000/")
Ana.Event = Event 
Ana.chnk = 1000
Ana.EventCache = True 
Ana.DumpPickle = True
#Ana.EventStop = 100
Ana.Launch()

nevents = 0
C1events = 0 
C2events = 0
C3events = 0
C4events = 0
C5events = 0
C6events = 0

topaccept = 0
toplep = 0
tophad = 0
topleptj = 0
ntops = 0

accept = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
leptonic = [11, 12, 13, 14]
Data = []
for i in Ana:
    event = i.Trees["nominal"]
    nevents += 1        
    stringR = {"Lep" : [], "Had" : []}
    
    ntops += len(event.Tops)
    C1Fail = False
    for t in event.Tops:
        if len([k.pdgid for k in t.Children if abs(k.pdgid) not in accept]) > 0:
            C1Fail = True
            continue
        topaccept += 1
        lp = "Lep" if sum([1 for k in t.Children if abs(k.pdgid) in leptonic]) > 0 else "Had"
        stringR[lp].append(t)

        if lp == "Lep":
            toplep += 1
    
        if lp == "Had" and len(t.TruthJets) == 3:
            tophad += 1
        if lp == "Lep" and len(t.TruthJets) == 1:
            topleptj += 1
    
    # Condition - 1: All tops decay either hadronically or leptonically 
    if C1Fail: 
        C1events += 1

    # Condition - 2: There are exactly 2 had and leptonic tops
    if len([1 for k in stringR if len(stringR[k]) != 2]) > 0:
        C2events += 1

    # Condition - 3: one lep and hadronic resonance top
    res = {k : t for k in stringR for t in stringR[k] if t.FromRes == 1}
    if len(res) != 2:
        C3events += 1

    # Condition - 4: All truth jets are matched to 1 or 0 tops
    if len([1 for tj in event.TruthJets if len(tj.Tops) > 1]):
        C4events += 1
    
    # Condition - 5: Leptonic top is matched to exactly one 
    if "Lep" not in res:
        C5events += 1
    elif len(res["Lep"].TruthJets) != 1:
        C5events += 1

    # Condition - 6: All had tops have at least 1 truth jet matched to them 
    if len([1 for t in stringR["Had"] if len(t.TruthJets) == 0]) != 0:
        C6events += 1
    continue 
    c = [t for t in stringR["Lep"] if t.FromRes == 1][0]
    c = [k for k in c.Children if abs(k.pdgid) in leptonic]
    res["Lep"].TruthJets += c

    res = sum([tj for k in res for tj in res[k].TruthJets]).CalculateMass()
    Data.append(res)


print("-> Tops Accepted: " + str(topaccept))
print("-> Tops Had (3-truth jets) " + str(tophad))
print("-> Tops Leptonic (no constraint on tj) " + str(toplep))
print("-> Tops Leptonic (1-truth jet) " + str(topleptj))
print("-> nTops (unconditional) " + str(ntops))
print("-> Loss - Condition 1: " + str(float(C1events)))
print("-> Loss - Condition 2: " + str(float(C2events)))
print("-> Loss - Condition 3: " + str(float(C3events)))
print("-> Loss - Condition 4: " + str(float(C4events)))
print("-> Loss - Condition 5: " + str(float(C5events)))
print("-> Loss - Condition 6: " + str(float(C6events)))
Plot = {
            "Title" : "Reconstructed Resonance Invariant Mass",
            "xMax" : 1500, 
            "xMin" : 0,
            "xBins" : 200,
            "xTitle" : "Mass (GeV)", 
            "Style" : "ATLAS",
            "Filename" : "Selection",
            "xData" : Data
        }
x = TH1F(**Plot)
x.SaveFigure()
