from AnalysisTopGNN.Plotting import TH1F, TH2F, CombineTH1F

def TemplatePlotsTH1F(x):
    Plots = {
                "NEvents" : x.NEvents, 
                "ATLASLumi" : x.Luminosity, 
                "Style" : "ATLAS", 
                "OutputDirectory" : "./Figures/EventNeutrino", 
                "yTitle" : "Entries (a.u.)", 
                "yMin" : 0, "xMin" : 0
            }
    return Plots

def TemplatePlotsTH2F(x):
    Plots = {
                "NEvents" : x.NEvents, 
                "ATLASLumi" : x.Luminosity, 
                "Style" : "ATLAS", 
                "OutputDirectory" : "./Figures/EventNeutrino", 
                "yMin" : 0, "xMin" : 0
            }
    return Plots



def EventNuNuSolutions(x):
    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Title"] = "Number of Neutrino Reconstruction Solutions"
    Plots_["xTitle"] = "Number of Solutions"
    Plots_["Histograms"] = []
    for i in x.NuNuSolutions:
        Plots = {}
        Plots["Title"] = i
        Plots["xData"] = x.NuNuSolutions[i]
        thc = TH1F(**Plots)
        Plots_["Histograms"].append(thc)
    Plots_["xStep"] = 1
    Plots_["xBinCentering"] = True
    Plots_["Filename"] = "Number-of-solutions"
    tc = CombineTH1F(**Plots_)
    tc.SaveFigure()
    
    # No Rotation
    Plots = TemplatePlotsTH2F(x)
    Plots["Title"] = "Delta Missing MET in Cartesian Coordinate System - No Rotation (Truth Neutrinos)"
    Plots["xTitle"] = "Missing Energy - x (GeV)"
    Plots["yTitle"] = "Missing Energy - y (GeV)"
    Plots["xStep"] = 20
    Plots["yStep"] = 20
    Plots["xMin"] = -500
    Plots["xMax"] = 500
    Plots["yMin"] = -500
    Plots["yMax"] = 500
    Plots["xScaling"] = 4
    Plots["yScaling"] = 2
    Plots["xData"] = x.Truth_MET_xy_Delta["No-Rotation-x"]
    Plots["yData"] = x.Truth_MET_xy_Delta["No-Rotation-y"]

    Plots["Filename"] = "Delta-Missing-MET-NoRotation"
    th = TH2F(**Plots)
    th.SaveFigure()

    # With Rotation
    Plots = TemplatePlotsTH2F(x)
    Plots["Title"] = "Delta Missing MET in Cartesian Coordinate System - Rotated (Truth Neutrinos)"
    Plots["xTitle"] = "Missing Energy - x (GeV)"
    Plots["yTitle"] = "Missing Energy - y (GeV)"
    Plots["xStep"] = 20
    Plots["yStep"] = 20
    Plots["xScaling"] = 4
    Plots["yScaling"] = 2
    Plots["xMin"] = -500
    Plots["xMax"] = 500
    Plots["yMin"] = -500
    Plots["yMax"] = 500
    Plots["xData"] = x.Truth_MET_xy_Delta["Rotation-x"]
    Plots["yData"] = x.Truth_MET_xy_Delta["Rotation-y"]
    Plots["Filename"] = "Delta-Missing-MET-Rotation"
    th = TH2F(**Plots)
    th.SaveFigure()

    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Title"] = "Reconstructed Top Mass Difference From \n Reconstructed Neutrinos Without Rotation"
    Plots_["xTitle"] = r"$\Delta$-($M_{top}$ - $M_{reco}$) (GeV)"
    Plots_["Histograms"] = []
    for i in x.TopMassDelta["No-Rotation"]:
        Plots = {}
        Plots["Title"] = "n-Sol: " + str(i)
        Plots["xData"] = x.TopMassDelta["No-Rotation"][i]
        Plots["xBins"] = 400
        thc = TH1F(**Plots)
        Plots_["Histograms"].append(thc)
    Plots_["xStep"] = 50
    Plots_["xMax"] = 200
    Plots_["xMin"] = -200
    Plots_["Filename"] = "Top-Mass-Delta-NoRotation"
    tc = CombineTH1F(**Plots_)
    tc.SaveFigure()

    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Title"] = "Reconstructed Top Mass Difference From \n Reconstructed Neutrinos With Rotation"
    Plots_["xTitle"] = r"$\Delta$-($M_{top}$ - $M_{reco}$) (GeV)"
    Plots_["Histograms"] = []
    for i in x.TopMassDelta["Rotation"]:
        Plots = {}
        Plots["Title"] = "n-Sol: " + str(i)
        Plots["xData"] = x.TopMassDelta["Rotation"][i]
        Plots["xBins"] = 400
        thc = TH1F(**Plots)
        Plots_["Histograms"].append(thc)
    Plots_["xStep"] = 50
    Plots_["xMax"] = 200
    Plots_["xMin"] = -200
    Plots_["Filename"] = "Top-Mass-Delta-Rotation"
    tc = CombineTH1F(**Plots_)
    tc.SaveFigure()

    # With Rotation
    Plots = TemplatePlotsTH2F(x)
    Plots["Title"] = "Ratio of Observed MET and Truth Neutrinos With and Without Reconstruction"
    Plots["xTitle"] = "Rotation (a.u.)"
    Plots["yTitle"] = "No-Rotation (a.u.)"
    Plots["xStep"] = 0.5
    Plots["yStep"] = 0.5
    Plots["xScaling"] = 2
    Plots["yScaling"] = 2
    Plots["xMin"] = 0
    Plots["xMax"] = 10
    Plots["yMin"] = 0
    Plots["yMax"] = 10
    Plots["xData"] = x.Truth_MET_NuNu_Delta["Rotation"]
    Plots["yData"] = x.Truth_MET_NuNu_Delta["No-Rotation"]
    Plots["Filename"] = "MET-Ratio"
    th = TH2F(**Plots)
    th.SaveFigure()


