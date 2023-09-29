from AnalysisG.Plotting import TH1F, TH2F, CombineTH1F

def TemplatePlotsTH1F(x):
    Plots = {
                "NEvents" : x.NEvents, 
                "ATLASLumi" : x.Luminosity, 
                "Style" : "ATLAS", 
                "OutputDirectory" : "./Figures/" + x.__class__.__name__, 
                "yTitle" : "Entries (a.u.)", 
            }
    return Plots

def TemplatePlotsTH2F(x):
    Plots = {
                "NEvents" : x.NEvents, 
                "ATLASLumi" : x.Luminosity, 
                "Style" : "ATLAS", 
                "OutputDirectory" : "./Figures/" + x.__class__.__name__, 
                "yMin" : 0, "xMin" : 0
            }
    return Plots



def EventNuNuSolutions(x):
    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Title"] = "Number of Reconstructed Neutrino Solutions"
    Plots_["xTitle"] = "Number of Solutions"
    Plots_["Histograms"] = []
    for i in x.NuNuSolutions:
        Plots = {}
        Plots["Title"] = i
        Plots["xData"] = x.NuNuSolutions[i]
        Plots_["Histograms"].append(TH1F(**Plots))
    Plots_["xStep"] = 1
    Plots_["xMin"] = -1
    Plots_["xBins"] = 6
    Plots_["xMax"] = 5
    Plots_["xBinCentering"] = True
    Plots_["Alpha"] = 0.1
    Plots_["Filename"] = "Figure_2.1a"
    tc = CombineTH1F(**Plots_)
    tc.SaveFigure()
    
    # No Rotation
    Plots = TemplatePlotsTH2F(x)
    Plots["Title"] = "$\Delta$ Missing MET in Cartesian Coordinate System \n No Rotation (Truth Neutrinos)"
    Plots["xTitle"] = "Missing Energy - x (GeV)"
    Plots["yTitle"] = "Missing Energy - y (GeV)"
    Plots["xStep"] = 50
    Plots["xBins"] = 250
    Plots["yBins"] = 250
    Plots["yStep"] = 50
    Plots["xMin"] = -500
    Plots["xMax"] = 500
    Plots["yMin"] = -500
    Plots["yMax"] = 500
    Plots["xData"] = x.Truth_MET_xy_Delta["No-Rotation-x"]
    Plots["yData"] = x.Truth_MET_xy_Delta["No-Rotation-y"]

    Plots["Filename"] = "Figure_2.1b"
    th = TH2F(**Plots)
    th.SaveFigure()

    # With Rotation
    Plots = TemplatePlotsTH2F(x)
    Plots["Title"] = "$\Delta$ Missing MET in Cartesian Coordinate System \n Rotated (Truth Neutrinos)"
    Plots["xTitle"] = "Missing Energy - x (GeV)"
    Plots["yTitle"] = "Missing Energy - y (GeV)"
    Plots["xStep"] = 50
    Plots["xBins"] = 250
    Plots["yBins"] = 250
    Plots["yStep"] = 50
    Plots["xMin"] = -500
    Plots["xMax"] = 500
    Plots["yMin"] = -500
    Plots["yMax"] = 500
    Plots["xData"] = x.Truth_MET_xy_Delta["Rotation-x"]
    Plots["yData"] = x.Truth_MET_xy_Delta["Rotation-y"]
    Plots["Filename"] = "Figure_2.2b"
    th = TH2F(**Plots)
    th.SaveFigure()
    
    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Title"] = "Difference between Truth Invariant Top Mass and \n Reconstructed Invariant Top Mass from Non Rotated Neutrinos"
    Plots_["xTitle"] = r"($M_{top}$ - $M_{reco}$) (GeV)"
    Plots_["Histograms"] = []
    for i in x.TopMassDelta["No-Rotation"]:
        Plots = {}
        Plots["Title"] = "n-Sol: " + str(i)
        Plots["xData"] = x.TopMassDelta["No-Rotation"][i]
        Plots_["Histograms"].append(TH1F(**Plots))
    Plots_["xStep"] = 10
    Plots_["xBins"] = 400
    Plots_["IncludeOverflow"] = True
    Plots_["yMin"] = 1
    Plots_["Logarithmic"] = True
    Plots_["xMax"] = 100
    Plots_["xMin"] = -100
    Plots_["Filename"] = "Figure_2.1c"
    tc = CombineTH1F(**Plots_)
    tc.SaveFigure()

    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Title"] = "Reconstructed Top Mass Difference From \n Reconstructed Neutrinos With Rotation"
    Plots_["xTitle"] = r"($M_{top}$ - $M_{reco}$) (GeV)"
    Plots_["Histograms"] = []
    for i in x.TopMassDelta["Rotation"]:
        Plots = {}
        Plots["Title"] = "n-Sol: " + str(i)
        Plots["xData"] = x.TopMassDelta["Rotation"][i]
        thc = TH1F(**Plots)
        Plots_["Histograms"].append(thc)
    Plots_["xStep"] = 10
    Plots_["xBins"] = 400
    Plots_["IncludeOverflow"] = True
    Plots_["yMin"] = 1
    Plots_["Logarithmic"] = True
    Plots_["xMax"] = 100
    Plots_["xMin"] = -100   
    Plots_["Filename"] = "Figure_2.2c"
    tc = CombineTH1F(**Plots_)
    tc.SaveFigure()

    # With Rotation
    Plots = TemplatePlotsTH2F(x)
    Plots["Title"] = "Ratio of Observed MET and Truth Neutrinos With and Without Rotation"
    Plots["xTitle"] = "Neutrino Reconstruction with Top Children Rotated into 4-Top System Rotation (a.u.)"
    Plots["yTitle"] = "Neutrino Reconstruction with No-Rotation (a.u.)"
    Plots["xStep"] = 0.5
    Plots["yStep"] = 0.5
    Plots["xScaling"] = 2
    Plots["yScaling"] = 2
    Plots["xMin"] = 0
    Plots["xMax"] = 10
    Plots["yMin"] = 0
    Plots["yMax"] = 10
    Plots["xBins"] = 100
    Plots["yBins"] = 100
    Plots["xData"] = x.Truth_MET_NuNu_Delta["Rotation"]
    Plots["yData"] = x.Truth_MET_NuNu_Delta["No-Rotation"]
    Plots["Filename"] = "Figure_2.1d"
    th = TH2F(**Plots)
    th.SaveFigure()


