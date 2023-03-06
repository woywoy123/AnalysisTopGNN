from AnalysisTopGNN import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.IO import PickleObject, UnpickleObject
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F

def PlotTemplate(nevents, lumi):
    Plots = {
                "yTitle" : "Entries (a.u.)",
                "xMin" : 0, 
                "yMin" : 0, 
                "xMax" : None,
                "xBins" : None,
                "OutputDirectory" : "./Figures_Dilepton_cutflow_EventStop100/", 
                "Style" : "ATLAS",
                "ATLASLumi" : lumi,
                "NEvents" : nevents
            }
    return Plots

direc = "/eos/home-t/tnommens/Processed/Dilepton/ttH_tttt_m1000"
#direc = "/eos/user/e/elebouli/BSM4tops/ttH_tttt_m1000_tmp"
Ana = Analysis()
Ana.InputSample("bsm1000", direc)
Ana.Event = Event
Ana.EventStop = 100
Ana.ProjectName = "Dilepton" + (f"_EventStop{Ana.EventStop}" if Ana.EventStop else "") 
Ana.EventCache = True
Ana.DumpPickle = True 
Ana.chnk = 100
Ana.Launch()

cutflow_children = {"Initial": 0, "SS2L": 0, "4b": 0, "4q": 0}
cutflow_truthjets = {"Initial": 0, "SS2L": 0, "4b": 0, "4j": 0}
nevents = 0
lumi = 0

for ev in Ana:
        
    event = ev.Trees["nominal"]
    nevents += 1

    lquarks = []
    bquarks = []
    leptons = []
    for p in event.TopChildren:
        if abs(p.pdgid) < 5:
            lquarks.append(p)
        elif abs(p.pdgid) == 5:
            bquarks.append(p)
        elif abs(p.pdgid) in [11, 13, 15]:
            leptons.append(p)

    ljets = []
    bjets = []
    topTJ = [l for t in event.Tops for l in t.TruthJets]
    for tj in topTJ:
        if tj.is_b:
            bjets.append(tj)
        else:
            ljets.append(tj)

    if len(ljets) > 4:
        ljets = sorted(ljets, key=lambda p: p.pt, reverse=True)[0:4]
    if len(bjets) > 4:
        bjets = sorted(bjets, key=lambda p: p.pt, reverse=True)[0:4]
    
    cutflow_children["Initial"] += 1
    cutflow_truthjets["Initial"] += 1

    cutflow_children["SS2L"] += 1 if len(leptons) == 2 and leptons[0].charge == leptons[1].charge else 0
    cutflow_truthjets["SS2L"] += 1 if len(leptons) == 2 and leptons[0].charge == leptons[1].charge else 0

    cutflow_children["4b"] += 1 if len(leptons) == 2 and leptons[0].charge == leptons[1].charge and len(bquarks) == 4 else 0
    cutflow_truthjets["4b"] += 1 if len(leptons) == 2 and leptons[0].charge == leptons[1].charge and len(bjets) == 4 else 0

    cutflow_children["4q"] += 1 if len(leptons) == 2 and leptons[0].charge == leptons[1].charge and len(bquarks) == 4 and len(lquarks) == 4 else 0
    cutflow_truthjets["4j"] += 1 if len(leptons) == 2 and leptons[0].charge == leptons[1].charge and len(bjets) == 4 and len(ljets) == 4 else 0

Plots = PlotTemplate(nevents, lumi)
Plots["Title"] = "Cutflow using top children" 
Plots["xTitle"] = "Cut"
Plots["xData"] = [i for i in range(len(cutflow_children))]
Plots["xTickLabels"] = [cut + " (" + str(cutflow_children[cut]) + ")" for cut in cutflow_children]
Plots["xBinCentering"] = True 
Plots["xStep"] = 1
Plots["xWeights"] = [i for i in cutflow_children.values()]
Plots["Filename"] = "Cutflow_children"
Plots["yTitle"] = "Number of events"
x = TH1F(**Plots)
x.SaveFigure()

Plots = PlotTemplate(nevents, lumi)
Plots["Title"] = "Cutflow using truth jets" 
Plots["xTitle"] = "Cut"
Plots["xData"] = [i for i in range(len(cutflow_truthjets))]
Plots["xTickLabels"] = [cut + " (" + str(cutflow_truthjets[cut]) + ")" for cut in cutflow_truthjets]
Plots["xBinCentering"] = True 
Plots["xStep"] = 1
Plots["xWeights"] = [i for i in cutflow_truthjets.values()]
Plots["Filename"] = "Cutflow_truthjets"
Plots["yTitle"] = "Number of events"
x = TH1F(**Plots)
x.SaveFigure()


