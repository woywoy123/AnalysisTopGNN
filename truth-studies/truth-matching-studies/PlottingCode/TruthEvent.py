from AnalysisG.Plotting import TH1F, TH2F

def TemplatePlotsTH1F(x):
    Plots = {
                "NEvents" : x.TotalEvents,
                "ATLASLumi" : x.Luminosity,
                "Style" : "ATLAS",
                "OutputDirectory" : "./Figures/" + x.__class__.__name__,
                "yTitle" : "Entries (a.u.)",
                "yMin" : 0, "xMin" : 0
            }
    return Plots

def TemplatePlotsTH2F(x):
    Plots = {
                "NEvents" : x.TotalEvents,
                "ATLASLumi" : x.Luminosity,
                "Style" : "ATLAS",
                "OutputDirectory" : "./Figures/" + x.__class__.__name__,
                "yMin" : 0, "xMin" : 0
            }
    return Plots

def EventNTruthJetAndJets(x):

    # Njets vs Ntruthjets
    Plots = TemplatePlotsTH2F(x)
    Plots["Title"] = "Number of Truth-Jets vs Reconstructed Jets"
    Plots["xTitle"] = "n-TruthJets"
    Plots["yTitle"] = "n-Jets"
    Plots["xStep"] = 1
    Plots["yStep"] = 1
    Plots["xMax"] = 40
    Plots["yMax"] = 40
    Plots["xBins"] = 40
    Plots["yBins"] = 40
    Plots["xData"] = x.TruthJets
    Plots["yData"] = x.Jets

    Plots["Filename"] = "Figure_0.1a"
    th = TH2F(**Plots)
    th.SaveFigure()

    # MET vs N-Leptons
    dic = {}
    for i, j in zip(x.nLep, x.MET):
        if i not in dic: dic[i] = []
        dic[i].append(j)

    Plots = TemplatePlotsTH1F(x)
    Plots["Title"] = "n-Leptonic Truth Children vs Missing Transverse Momenta"
    Plots["xTitle"] = "Missing Transverse Momenta (GeV)"
    Plots["Histograms"] = []
    for i in dic:
        _plt = {}
        _plt["Title"] = str(i) + "-Lep"
        _plt["xData"] = dic[i]
        Plots["Histograms"].append(TH1F(**_plt))
    Plots["xBins"] = 1000
    Plots["xStep"] = 100
    Plots["Filename"] = "Figure_0.1b"
    th = TH1F(**Plots)
    th.SaveFigure()

def EventMETImbalance(x):
    Plots = TemplatePlotsTH2F(x)
    Plots["Title"] = "4-Top System Transverse Momentum as a \n Function of Pz (Momentum Down Beam Pipe)"
    Plots["xTitle"] = "Momentum Vector in Z-direction (GeV)"
    Plots["yTitle"] = "Transverse Momentum (GeV)"
    Plots["xStep"] = 200
    Plots["yStep"] = 200
    Plots["xMin"] = -1000
    Plots["xMax"] = 1000
    Plots["yMin"] = 0
    Plots["yMax"] = 1000
    Plots["xBins"] = 200
    Plots["yBins"] = 200
    Plots["xData"] = x.Pz_4Tops
    Plots["yData"] = x.PT_4Tops
    Plots["Filename"] = "Figure_0.1c"
    th = TH2F(**Plots)
    th.SaveFigure()

    Plots = {}
    Plots["Title"] = "4-Tops"
    Plots["xData"] = x.Top4_angle
    tht = TH1F(**Plots)

    Plots = {}
    Plots["Title"] = "4-TopChildren"
    Plots["xData"] = x.Children_angle
    thc = TH1F(**Plots)

    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Title"] = "Relative Angle Between 4-Top \nTransverse Momentum System and Beam Pipe"
    Plots_["xTitle"] = "Angle atan(PT/Pz) (Rad)"
    Plots_["Histograms"] = [tht, thc]
    Plots_["xStep"] = 0.20002
    Plots_["xMin"] = 0
    Plots_["xBins"] = 400
    Plots_["xMax"] = 2
    Plots_["yMax"] = 0.06
    Plots_["OverFlow"] = True
    Plots_["Normalize"] = True
    Plots_["Filename"] = "Figure_0.1d"
    tc = TH1F(**Plots_)
    tc.SaveFigure()

    Plots = {}
    Plots["Title"] = "4-Tops"
    Plots["xData"] = x.r_Top4_angle
    tht = TH1F(**Plots)

    Plots = {}
    Plots["Title"] = "4-TopChildren"
    Plots["xData"] = x.r_Children_angle
    thc = TH1F(**Plots)

    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Title"] = "Relative Angle Between 4-Top Transverse Momentum System \n and Beam Pipe after Rotating into 4-Top System"
    Plots_["xTitle"] = "Angle atan(PT/Pz) (Rad)"
    Plots_["Histograms"] = [tht, thc]
    Plots_["xStep"] = 0.2
    Plots_["xMin"] = 0
    Plots_["xMax"] = 2
    Plots_["xBins"] = 400
    Plots_["yMax"] = 0.06
    Plots_["Normalize"] = True
    Plots_["Filename"] = "Figure_0.2d"
    tc = TH1F(**Plots_)
    tc.SaveFigure()

    Plots = {}
    Plots["Title"] = "Measured"
    Plots["xData"] = x.MET
    tht = TH1F(**Plots)

    Plots = {}
    Plots["Title"] = "Truth-Neutrino"
    Plots["xData"] = x.NeutrinoET
    thc = TH1F(**Plots)

    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Title"] = "Missing Transverse Energy - Before Rotation"
    Plots_["xTitle"] = "Missing Transverse Energy (GeV)"
    Plots_["Histograms"] = [tht, thc]
    Plots_["xStep"] = 100
    Plots_["xMin"] = 0
    Plots_["xMax"] = 1000
    Plots_["yMax"] = 0.02
    Plots_["Normalize"] = True
    Plots_["Filename"] = "Figure_0.1e"
    tc = TH1F(**Plots_)
    tc.SaveFigure()

    Plots = {}
    Plots["Title"] = "Measured"
    Plots["xMin"] = 0
    Plots["xData"] = x.MET
    tht = TH1F(**Plots)

    Plots = {}
    Plots["Title"] = "Truth-Neutrino"
    Plots["xMin"] = 0
    Plots["xData"] = x.r_NeutrinoET
    thc = TH1F(**Plots)

    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Title"] = "Missing Transverse Energy - After Rotating Neutrinos"
    Plots_["xTitle"] = "Missing Transverse Energy (GeV)"
    Plots_["Histograms"] = [tht, thc]
    Plots_["xStep"] = 100
    Plots_["xMin"] = 0
    Plots_["xMax"] = 1000
    Plots_["yMax"] = 0.02
    Plots_["Normalize"] = True
    Plots_["Filename"] = "Figure_0.2e"
    tc = TH1F(**Plots_)
    tc.SaveFigure()

    Plots = {}
    Plots["Title"] = r"Measured - $\Sigma \nu$ (No Rotation)"
    Plots["xData"] = x.METDelta
    thc1 = TH1F(**Plots)

    Plots = {}
    Plots["Title"] = r"Measured - $\Sigma \nu$ (Rotated)"
    Plots["xData"] = x.r_METDelta
    thc2 = TH1F(**Plots)

    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Histograms"] = [thc1, thc2]
    Plots_["Title"] = r"Missing Transverse Energy Difference"
    Plots_["xTitle"] = "$\Delta$ Missing Transverse Energy (GeV)"
    Plots_["xMin"] = -500
    Plots_["xMax"] = 500
    Plots_["xStep"] = 50
    Plots_["Normalize"] = True
    Plots_["yMax"] = 0.02
    Plots_["Filename"] = "Figure_0.3e"
    tc = TH1F(**Plots_)
    tc.SaveFigure()


