from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.Particles import Particles
from AnalysisTopGNN.IO import PickleObject, UnpickleObject
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F

_charged_leptons = [11, 13, 15]
_observable_leptons = [11, 13]

def PlotTemplate(nevents, lumi):
    Plots = {
                "yTitle" : "Entries (a.u.)",
                "xMin" : 0, 
                "yMin" : 0, 
                "xMax" : None,
                "xBins" : None,
                "OutputDirectory" : "./Figures/", 
                "Style" : "ATLAS",
                "ATLASLumi" : lumi,
                "NEvents" : nevents
            }
    return Plots


def Selection(Ana):

    numLeptons = {"0L": 0, "1L": 0, "2LOS": 0, "2LSS": 0, "3L": 0, "4L": 0}

    nevents = 0
    lumi = 0
    for ev in Ana:
        
        event = ev.Trees["nominal"]
        nevents += 1
        lumi += event.Lumi

        leptons = []
    
        for p in event.TopChildren:
            if abs(p.pdgid) in _observable_leptons:
                leptons.append(p)
            elif abs(p.pdgid) == 15:
                for c in p.Children:
                    # if abs(c.pdgid) in _observable_leptons:
                    #     leptons.append(c)
                    if isinstance(c, Particles.Electron) or isinstance(c, Particles.Muon):
                        leptons.append(c)

        if len(leptons) == 0: 
            numLeptons["0L"] += 1
        elif len(leptons) == 1:
            numLeptons["1L"] += 1
        elif len(leptons) == 2:
            if leptons[0].charge == leptons[1].charge: numLeptons["2LSS"] += 1
            else: numLeptons["2LOS"] += 1
        elif len(leptons) == 3:
            numLeptons["3L"] += 1
        else:
            numLeptons["4L"] += 1

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Lepton multiplicity" 
    Plots["xTitle"] = "Number of leptons"
    Plots["xTickLabels"] = ["0L (" +   str(numLeptons["0L"]    ) + ")", 
                            "1L (" +   str(numLeptons["1L"]    ) + ")",
                            "2LOS (" +   str(numLeptons["2LOS"]    ) + ")",
                            "2LSS (" +   str(numLeptons["2LSS"]    ) + ")", 
                            "3L (" +   str(numLeptons["3L"]    ) + ")",
                            "4L (" +   str(numLeptons["4L"]    ) + ")",]

    Plots["xData"] = [0, 1, 2, 3, 4, 5]
    Plots["xWeights"] = [numLeptons["0L"],    
                         numLeptons["1L"],    
                         numLeptons["2LOS"], 
                         numLeptons["2LSS"], 
                         numLeptons["3L"],
                         numLeptons["4L"]]
    Plots["xMin"] = 0
    Plots["xStep"] = 1
    Plots["xBinCentering"] = True 
    Plots["Filename"] = "LeptonChannel"
    F = TH1F(**Plots)
    F.SaveFigure()



    



 

