from AnalysisG.Plotting import TH1F, CombineTH1F

def PlotTemplate(x):
    Plots = {
                "yTitle" : "Entries (a.u.)",
                "xMin" : 0, 
                "yMin" : 0, 
                "xMax" : None,
                "xBins" : None,
                "OutputDirectory" : "./Figures/" + x.__class__.__name__, 
                "Style" : "ATLAS",
                "ATLASLumi" : x.Luminosity,
                "NEvents" : x.NEvents
            }
    return Plots

def ResonanceMassFromChildren(x):
    Plots = PlotTemplate(x)
    Plots["Title"] = "Reconstructed Invariant Scalar H Mass from Top Truth Children"
    Plots["xTitle"] = "Invariant Scalar H Mass (GeV)"
    Plots["xMin"] = 0
    Plots["xMax"] = 2000
    Plots["xStep"] = 100
    Plots["Filename"] = "Figure_2.1c"
    Plots["Histograms"] = []

    for i in x.ResonanceMass:
        if len(x.ResonanceMass[i]) == 0: continue
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = x.ResonanceMass[i]
        _Plots["xBins"] = 1000
        Plots["Histograms"].append(TH1F(**_Plots))
    X = CombineTH1F(**Plots)
    X.SaveFigure()



