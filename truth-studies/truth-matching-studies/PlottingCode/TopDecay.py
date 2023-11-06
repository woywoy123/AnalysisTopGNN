from AnalysisG.Plotting import TH1F, TH2F

def PlotTemplate(x):
    Plots = {
                "yTitle" : "Entries (a.u.)",
                "yMin" : 0,
                "xMax" : None,
                "OutputDirectory" : "./Figures/" + x.__class__.__name__,
                "Style" : "ATLAS",
                "ATLASLumi" : x.Luminosity,
                "NEvents" : x.TotalEvents
            }
    return Plots

def TopDecayModes(x):
    Plots = PlotTemplate(x)
    Plots["Title"] = "Decay Products of Tops"
    Plots["xTitle"] = "Symbol"
    Plots["yTitle"] = "Fraction of Times Top Decays Into PDGID"
    Plots["xLabels"] = {i : j for i, j in x.CounterPDGID.items()}
    Plots["xBinCentering"] = True
    Plots["Filename"] = "Figure_2.1a"
    plt = TH1F(**Plots)
    plt.SaveFigure()

    Plots = PlotTemplate(x)
    Plots["Title"] = "Reconstructed Invariant Top Mass from Immediate Decay Products"
    Plots["xTitle"] = "Invariant Top Mass (GeV)"
    Plots["xMin"] = 120
    Plots["xStep"] = 10
    Plots["xMax"] = 240
    Plots["xBins"] = 1000
    Plots["Filename"] = "Figure_2.1b"
    Plots["Histograms"] = []

    for i in x.TopMassTC:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = x.TopMassTC[i]
        Plots["Histograms"].append(TH1F(**_Plots))
    plt = TH1F(**Plots)
    plt.SaveFigure()


