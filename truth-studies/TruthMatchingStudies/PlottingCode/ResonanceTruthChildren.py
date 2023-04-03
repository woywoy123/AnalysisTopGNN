from AnalysisTopGNN.Plotting import TH1F, CombineTH1F

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

def ResonanceMassFromChildren(x)

    for i in x.ResonanceMass:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = TopMass[i]
        Plots["Histograms"].append(TH1F(**_Plots))
    X = CombineTH1F(**Plots)
    X.SaveFigure()

    Plots = PlotTemplate(x)
    Plots["Title"] = "Reconstructed Invariant Scalar H Mass from Top Truth Children"
    Plots["xTitle"] = "Invariant Scalar H Mass (GeV)"
    Plots["xBins"] = 1000
    Plots["xMin"] = 0
    Plots["xMax"] = 2000
    Plots["Filename"] = "Figure_2.1c"
    Plots["Histograms"] = []
