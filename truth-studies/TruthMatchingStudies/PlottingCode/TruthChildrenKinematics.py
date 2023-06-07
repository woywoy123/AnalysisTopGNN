from AnalysisTopGNN.Plotting import TH1F, CombineTH1F, TH2F

def PlotTemplate(x):
    Plots = {
                "yTitle" : "Entries (a.u.)",
                "xMin" : 0, 
                "yMin" : 0, 
                "xMax" : None,
                "xBins" : None,
                "OutputDirectory" : "./Figures/TruthChildrenKinematics", 
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
       
    Plots = PlotTemplate(x)
    Plots["Title"] = "$\Delta$R Between Parent Top and Hadronic-Leptonic Children."
    Plots["xTitle"] = "$\Delta$R"
    Plots["xStep"] = 0.2
    Plots["Filename"] = "Figure_2.1e"
    Plots["xScaling"] = 2.5
    Plots["Histograms"] = []
    
    for i in ["Lep", "Had"]:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = x.TopChildrenCluster[i]
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()

    Plots = PlotTemplate(x)
    Plots["Title"] = "$\Delta$R Clustering of Children Pair"
    Plots["xTitle"] = "$\Delta$R"
    Plots["xStep"] = 0.2
    Plots["Filename"] = "Figure_2.1f"
    Plots["xScaling"] = 2.5
    Plots["Stack"] = True
    Plots["yTitle"] = "Fraction of Cases (%)"
    Plots["Normalize"] = "%"
    Plots["Histograms"] = []
   
    s = [
            "Correct-Top-Res-Res", "False-Top-Res-Res", 
            "Correct-Top-Spec-Spec", "False-Top-Res-Spec", 
            "False-Top-Spec-Spec"
    ]
    for i in s:
        _Plots = {}
        _Plots["Title"] = i.replace("-Top", "")
        _Plots["xData"] = x.MatchedChildren[i]
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()

    Plots = PlotTemplate(x)
    Plots["Title"] = "$\Delta$R Between Decay Products of Mutual Top as a Function of Parent Top Transverse Momenta (Hadronic)"
    Plots["yTitle"] = "$\Delta$R"
    Plots["xTitle"] = "Transverse Momentum (GeV)"
    Plots["yStep"] = 0.2
    Plots["xStep"] = 50
    Plots["xScaling"] = 3
    Plots["yScaling"] = 3
    Plots["yMin"] = 0
    Plots["yMax"] = 6.6
    Plots["xMin"] = 0
    Plots["xMax"] = 1250
    Plots["yData"] = x.ChildrenCluster["Had-DelR"]
    Plots["xData"] = x.ChildrenCluster["Had-top-PT"]
    Plots["Filename"] = "Figure_2.1g"
    X = TH2F(**Plots)
    X.SaveFigure()

    Plots = PlotTemplate(x)
    Plots["Title"] = "$\Delta$R Between Decay Products of Mutual Top as a Function of Parent Top Transverse Momenta (Leptonic)"
    Plots["yTitle"] = "$\Delta$R"
    Plots["xTitle"] = "Transverse Momentum (GeV)"
    Plots["yStep"] = 0.2
    Plots["xStep"] = 50
    Plots["xScaling"] = 3
    Plots["yScaling"] = 3
    Plots["yMin"] = 0
    Plots["yMax"] = 6.6
    Plots["xMin"] = 0
    Plots["xMax"] = 1250
    Plots["yData"] = x.ChildrenCluster["Lep-DelR"]
    Plots["xData"] = x.ChildrenCluster["Lep-top-PT"]
    Plots["Filename"] = "Figure_2.1h"
    X = TH2F(**Plots)
    X.SaveFigure()

def Kinematics(x):
    Plots = PlotTemplate(x)
    Plots["Title"] = "Fractional Transverse Momenta Transferred\n to Decay Products from Parent Top"
    Plots["xTitle"] = "Fraction"
    Plots["xStep"] = 0.2
    Plots["xMax"] = 4
    Plots["Filename"] = "Figure_2.1i"
    Plots["Stack"] = True
    Plots["Histograms"] = []
    
    for i in x.FractionalPT:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = x.FractionalPT[i]
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()

    Plots = PlotTemplate(x)
    Plots["Title"] = "Fraction of Top Energy Transferred to Decay Products"
    Plots["xTitle"] = "Fraction"
    Plots["xStep"] = 0.2
    Plots["xMax"] = 4
    Plots["Filename"] = "Figure_2.1j"
    Plots["Stack"] = True
    Plots["Histograms"] = []
    
    for i in x.FractionalEnergy:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = x.FractionalEnergy[i]
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()


