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


def DeltaRChildren(x):
    Plots = PlotTemplate(x)
    Plots["Title"] = "$\Delta$R Between Truth Children Originating from Mutual Top"
    Plots["xTitle"] = "$\Delta$R"
    Plots["xStep"] = 0.2
    Plots["Filename"] = "Figure_2.1d"
    Plots["xScaling"] = 2.5
    Plots["Histograms"] = []
    
    for i in ["Res-DelR", "Spec-DelR"]:
        _Plots = {}
        _Plots["Title"] = i.split("-")[0]
        _Plots["xData"] = x.ChildrenCluster[i]
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    plt = CombineTH1F(**Plots)
    plt.SaveFigure()
        
    exit()

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "$\Delta$R Between Parent Top and Decay Products"
    Plots["xTitle"] = "$\Delta$R"
    Plots["xStep"] = 0.2
    Plots["Filename"] = "Figure_2.1f"
    Plots["xScaling"] = 2.5
    Plots["Histograms"] = []
    
    for i in TopChildrenCluster:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = TopChildrenCluster[i]
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "$\Delta$R Between Decay Products of Mutual Top \n as a Function of Parent Top Transverse Momenta"
    Plots["yTitle"] = "$\Delta$R"
    Plots["xTitle"] = "Transverse Momentum (GeV)"
    Plots["yStep"] = 0.2
    Plots["xStep"] = 25
    Plots["xScaling"] = 2.5
    Plots["yScaling"] = 2
    Plots["xMin"] = 0
    Plots["yMin"] = 0
    Plots["yData"] = ChildrenClusterPT["DelR"]
    Plots["xData"] = ChildrenClusterPT["PT"]
    Plots["Filename"] = "Figure_2.1g"
    X = TH2F(**Plots)
    X.SaveFigure()




