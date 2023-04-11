from AnalysisTopGNN.Plotting import TH1F, TH2F, CombineTH1F

def TemplatePlotsTH1F(x):
    Plots = {
                "NEvents" : x.NEvents, 
                "ATLASLumi" : x.Luminosity, 
                "Style" : "ATLAS", 
                "OutputDirectory" : "./Figures/TruthEvent", 
                "yTitle" : "Entries (a.u.)", 
                "yMin" : 0, "xMin" : 0
            }
    return Plots

def TemplatePlotsTH2F(x):
    Plots = {
                "NEvents" : x.NEvents, 
                "ATLASLumi" : x.Luminosity, 
                "Style" : "ATLAS", 
                "OutputDirectory" : "./Figures/TruthEvent", 
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
    Plots["xScaling"] = 2
    Plots["yScaling"] = 2
    Plots["xData"] = x.TruthJets
    Plots["yData"] = x.Jets

    Plots["Filename"] = "N-TruthJets_n-Jets"
    th = TH2F(**Plots)
    th.SaveFigure()

    # MET vs N-Leptons
    Plots = TemplatePlotsTH2F(x)
    Plots["Title"] = "n-Leptonic Truth Children vs Missing Transverse Momenta"
    Plots["xTitle"] = "n-Leptonic Truth Children"
    Plots["yTitle"] = "Missing Transverse Momenta (GeV)"
    Plots["xStep"] = 1
    Plots["yStep"] = 50
    Plots["xScaling"] = 2
    Plots["yScaling"] = 2
    Plots["xData"] = x.nLep
    Plots["yData"] = x.MET

    Plots["Filename"] = "MissingET_n-TruthLep"
    th = TH2F(**Plots)
    th.SaveFigure()

def EventMETImbalance(x):
    Plots = TemplatePlotsTH2F(x)
    Plots["Title"] = "4-Top System Transverse Momentum vs Pz (Momentum Down Beam Pipe)"
    Plots["xTitle"] = "Momentum Vector in Z-direction (GeV)"
    Plots["yTitle"] = "Transverse Momentum (GeV)"
    Plots["xStep"] = 100
    Plots["yStep"] = 50
    Plots["xScaling"] = 3
    Plots["yScaling"] = 2
    Plots["xData"] = x.Pz_4Tops
    Plots["yData"] = x.PT_4Tops
    Plots["Filename"] = "4-TopSystem-Pz_PT"
    th = TH2F(**Plots)
    th.SaveFigure()

    Plots = {}
    Plots["Title"] = "4-Tops"
    Plots["xBins"] = 400
    Plots["xData"] = x.Top4_angle
    tht = TH1F(**Plots)

    Plots = {}
    Plots["Title"] = "4-TopChildren"
    Plots["xBins"] = 400
    Plots["xData"] = x.Children_angle
    thc = TH1F(**Plots)

    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Title"] = "Relative Angle Between 4-Top \nTransverse Momentum System and Beam Pipe"
    Plots_["xTitle"] = "Angle atan(PT/Pz) (Rad)"
    Plots_["Histograms"] = [tht, thc]
    Plots_["xStep"] = 0.2
    Plots_["xMin"] = -1.8
    Plots_["xMax"] = 1.8
    Plots_["Filename"] = "AngleRelativeToBeamPipe"
    tc = CombineTH1F(**Plots_)
    tc.SaveFigure()

    Plots = {}
    Plots["Title"] = "4-Tops"
    Plots["xBins"] = 400
    Plots["xData"] = x.r_Top4_angle
    tht = TH1F(**Plots)

    Plots = {}
    Plots["Title"] = "4-TopChildren"
    Plots["xBins"] = 400
    Plots["xData"] = x.r_Children_angle
    thc = TH1F(**Plots)

    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Title"] = "Relative Angle Between 4-Top \nTransverse Momentum System and Beam Pipe after Rotation"
    Plots_["xTitle"] = "Angle atan(PT/Pz) (Rad)"
    Plots_["Histograms"] = [tht, thc]
    Plots_["xStep"] = 0.2
    Plots_["xMin"] = -1.8
    Plots_["xMax"] = 1.8
    Plots_["Filename"] = "AngleRelativeToBeamPipe-Rotated"
    tc = CombineTH1F(**Plots_)
    tc.SaveFigure()

    Plots = {}
    Plots["Title"] = "Measured"
    Plots["xBins"] = 400
    Plots["xMin"] = 0
    Plots["xData"] = x.MET
    tht = TH1F(**Plots)

    Plots = {}
    Plots["Title"] = "TruthNeutrino"
    Plots["xBins"] = 400
    Plots["xMin"] = 0
    Plots["xData"] = x.NeutrinoET
    thc = TH1F(**Plots)

    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Title"] = "Missing Transverse Energy - Before Rotation"
    Plots_["xTitle"] = "Missing Transverse Energy (GeV)"
    Plots_["Histograms"] = [tht, thc]
    Plots_["xStep"] = 100
    Plots_["xMin"] = 0
    Plots_["xMax"] = 1000
    Plots_["Filename"] = "MissingET"
    tc = CombineTH1F(**Plots_)
    tc.SaveFigure()


    Plots = {}
    Plots["xBins"] = 1000
    Plots["xData"] = x.METDelta
    thc = TH1F(**Plots)

    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Histograms"] = [thc]
    Plots_["Title"] = r"Missing Transverse Energy Difference (Measured - $\Sigma \nu$)"
    Plots_["xTitle"] = "$\Delta$ Missing Transverse Energy (GeV)"
    Plots_["xMin"] = -500
    Plots_["xMax"] = 500
    Plots_["xStep"] = 50
    Plots_["Filename"] = "Difference-MissingET"
    tc = CombineTH1F(**Plots_)
    tc.SaveFigure()


    Plots = {}
    Plots["Title"] = "Measured"
    Plots["xBins"] = 400
    Plots["xMin"] = 0
    Plots["xData"] = x.MET
    tht = TH1F(**Plots)

    Plots = {}
    Plots["Title"] = "TruthNeutrino"
    Plots["xBins"] = 400
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
    Plots_["Filename"] = "MissingET-Rotated"
    tc = CombineTH1F(**Plots_)
    tc.SaveFigure()


    Plots = {}
    Plots["xBins"] = 1000
    Plots["xData"] = x.r_METDelta
    thc = TH1F(**Plots)

    Plots_ = TemplatePlotsTH1F(x)
    Plots_["Histograms"] = [thc]
    Plots_["Title"] = r"Missing Transverse Energy Difference (Measured - $\Sigma \nu$) - Rotated"
    Plots_["xTitle"] = "$\Delta$ Missing Transverse Energy (GeV)"
    Plots_["xMin"] = -500
    Plots_["xMax"] = 500
    Plots_["xStep"] = 50
    Plots_["Filename"] = "difference-MissingET-Rotated"
    tc = CombineTH1F(**Plots_)
    tc.SaveFigure()
