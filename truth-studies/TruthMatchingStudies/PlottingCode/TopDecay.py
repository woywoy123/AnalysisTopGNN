from AnalysisTopGNN.Plotting import TH1F, TH2F, CombineTH1F


def PlotTemplate(x):
    Plots = {
                "yTitle" : "Entries (a.u.)",
                "xMin" : 0, 
                "yMin" : 0, 
                "xMax" : None,
                "xBins" : None,
                "OutputDirectory" : "./Figures/TopDecayModes", 
                "Style" : "ATLAS",
                "ATLASLumi" : x.Luminosity,
                "NEvents" : x.NEvents
            }
    return Plots

def TopDecayModes(x):
    Plots = PlotTemplate(x)
    Plots["Title"] = "Decay Products of Tops" 
    Plots["xTitle"] = "Symbol"
    Plots["yTitle"] = "Fraction of Times Top Decays Into PDGID"
    Plots["xTickLabels"] = list(x.CounterPDGID)
    Plots["xBinCentering"] = True 
    Plots["xStep"] = 1
    Plots["Normalize"] = False 
    Plots["xData"] = [i for i in range(len(x.CounterPDGID))]

    Plots["xWeights"] = [float(i / x.TopCounter) for i in x.CounterPDGID.values()]
    Plots["Filename"] = "Figure_2.1a"
    x = TH1F(**Plots)
    x.SaveFigure()
