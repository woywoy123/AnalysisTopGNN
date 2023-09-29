from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.IO import PickleObject, UnpickleObject
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F
import numpy as np
import math

def PlotTemplate(nevents, lumi):
    Plots = {
                "yTitle" : "Entries (a.u.)",
                "xMin" : 0, 
                "yMin" : 0, 
                "xMax" : None,
                "xBins" : None,
                "OutputDirectory" : "./testMET/", 
                "Style" : "ATLAS",
                "ATLASLumi" : lumi,
                "NEvents" : nevents
            }
    return Plots

direc = "/eos/user/e/elebouli/BSM4tops/ttH_tttt_m1000"
Ana = Analysis()
Ana.InputSample("tttt", direc)
Ana.Event = Event
Ana.EventStop = 100
Ana.ProjectName = "Dilepton" + (f"_EventStop{Ana.EventStop}" if Ana.EventStop else "")
Ana.Threads = 12
Ana.chnk = 1000
Ana.EventCache = True
Ana.DumpPickle = True
Ana.Launch()

nevents = 0
lumi = 0
MissingET = {"From ntuples": [], "From neg sum of truth objects": [], "From neg sum of truth objects incl rad": [], "From truth neutrinos": []}
MissingETDiff = {"From neg sum of truth objects": [], "From neg sum of truth objects incl rad": [], "From truth neutrinos": []}

for ev in Ana:
    
    event = ev.Trees["nominal"]
    nevents += 1
    lumi += event.Lumi

    lquarks = []
    bquarks = []
    leptons = []
    neutrinos = []

    for p in event.TopChildren:
        if abs(p.pdgid) < 5:
            lquarks.append(p)
        elif abs(p.pdgid) == 5:
            bquarks.append(p)
        elif abs(p.pdgid) in [11, 13, 15]:
            leptons.append(p)
        elif abs(p.pdgid) in [12, 14, 16]:
            neutrinos.append(p)

    all_particles = sum(leptons + bquarks + lquarks)
    met = all_particles.pt / 1000.

    ## This gives the same result as above
    # neg_sum_x = [-p.pt * np.cos(p.phi) for p in (leptons + bquarks + lquarks)]
    # neg_sum_y = [-p.pt * np.sin(p.phi) for p in (leptons + bquarks + lquarks)]
    # met_x2 = sum(neg_sum_x)
    # met_y2 = sum(neg_sum_y)
    # met2 = math.sqrt(pow(met_x2, 2) + pow(met_y2, 2))

    all_particles_withRad = sum([p for p in event.TopChildren if p.pdgid not in [12, 14, 16]])
    met_withRad = all_particles_withRad.pt / 1000.

    event_met = event.met / 1000.

    MissingET["From ntuples"].append(event_met)
    MissingET["From neg sum of truth objects"].append(met)
    MissingET["From neg sum of truth objects incl rad"].append(met_withRad)
    MissingETDiff["From neg sum of truth objects"].append(met - event_met)
    MissingETDiff["From neg sum of truth objects incl rad"].append(met_withRad - event_met)
    if len(neutrinos) > 0:
        nus = sum(neutrinos)
        MissingET["From truth neutrinos"].append(nus.pt/1000.)
        MissingETDiff["From truth neutrinos"].append(nus.pt/1000. - event_met)


Plots = PlotTemplate(nevents, lumi)
Plots["Title"] = "Missing Transverse Energy"
Plots["xTitle"] = "MET (GeV)"
Plots["xBins"] = 200
Plots["xMin"] = 0
Plots["xMax"] = 1000
Plots["Filename"] = "MET"
Plots["Histograms"] = []

for i in MissingET:
    _Plots = {}
    _Plots["Title"] = i
    _Plots["xData"] = MissingET[i]
    Plots["Histograms"].append(TH1F(**_Plots))

X = CombineTH1F(**Plots)
X.SaveFigure()

Plots = PlotTemplate(nevents, lumi)
Plots["Title"] = "Missing Transverse Energy Difference"
Plots["xTitle"] = "MET calculated - MET from ntuples (GeV)"
Plots["xBins"] = 200
Plots["xMin"] = -500
Plots["xMax"] = 500
Plots["Filename"] = "METDiff"
Plots["Histograms"] = []

for i in MissingETDiff:
    _Plots = {}
    _Plots["Title"] = i
    _Plots["xData"] = MissingETDiff[i]
    Plots["Histograms"].append(TH1F(**_Plots))

X = CombineTH1F(**Plots)
X.SaveFigure()

