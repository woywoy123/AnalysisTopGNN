from AnalysisTopGNN.Plotting import TH1F, CombineTH1F

def PlotTemplate(nevents, lumi):
    Plots = {
                "Style" : "ATLAS",
                "NEvents" : nevents, 
                "ATLASLumi" : lumi,
                "OutputDirectory" : "./Figures/ResonanceTruthTops", 
                "yTitle" : "Entries (a.u.)",
                "yMin" : 0,
            }
    return Plots

def ResonanceDecayModes(x):
    Plots = PlotTemplate(x.NEvents, x.Luminosity)
    Plots["Title"] = "Decay Mode of the Resonance" 
    Plots["xTitle"] = "Decay Mode of scalar H (a.u)"
    Plots["xTickLabels"] = [
            "Lep (" + str(x.ResDecayMode["L"]) + ")", 
            "Had (" + str(x.ResDecayMode["H"]) + ")",
            "Had-Had (" + str(x.ResDecayMode["HH"]) + ")",
            "Had-Lep (" + str(x.ResDecayMode["HL"]) + ")", 
            "Lep-Lep (" + str(x.ResDecayMode["LL"]) + ")"]

    Plots["xData"] = [0, 1, 2, 3, 4]
    Plots["xWeights"] = [
            x.ResDecayMode["L"], x.ResDecayMode["H"], 
            x.ResDecayMode["HH"], x.ResDecayMode["HL"], x.ResDecayMode["LL"]]
    Plots["xMin"] = 0
    Plots["xStep"] = 1
    Plots["xBinCentering"] = True 
    Plots["Filename"] = "Figure_1.1a"
    F = TH1F(**Plots)
    F.SaveFigure()
    
    Plots = PlotTemplate(x.NEvents, x.Luminosity)
    Plots["Title"] = "Decay Mode of all Tops" 
    Plots["xTitle"] = "Decay Mode of Tops (a.u)"
    Plots["xTickLabels"] = [
            "Res-Lep (" +  str(x.TopDecayMode["Res-L"] ) + ")", 
            "Res-Had (" +  str(x.TopDecayMode["Res-H"] ) + ")", 
            "Spec-Lep (" + str(x.TopDecayMode["Spec-L"]) + ")", 
            "Spec-Had (" + str(x.TopDecayMode["Spec-H"]) + ")"]

    Plots["xData"] = [0, 1, 2, 3]
    Plots["xWeights"] = [
            x.TopDecayMode["Res-L"], x.TopDecayMode["Res-H"],
            x.TopDecayMode["Spec-L"], x.TopDecayMode["Spec-H"]]
    Plots["xMin"] = 0
    Plots["xStep"] = 1
    Plots["xBinCentering"] = True 
    Plots["Filename"] = "Figure_1.1b"
    F = TH1F(**Plots)
    F.SaveFigure()

def ResonanceMassFromTops(x):
    Plots = PlotTemplate(x.NEvents, x.Luminosity)
    Plots["Histograms"] = []
    for k in x.ResDecayMode:
        _Plots = {}
        dec = ""
        if k == "HH":
            dec = "Hadronic"
        if k == "HL":
            dec = "Hadronic-Leptonic"
        if k == "LL":
            dec = "Leptonic"
        if dec == "":
            continue 
        _Plots["Title"] = dec
        _Plots["xData"] = x.ResDecayMode[k]
        _Plots["xBins"] = 100
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    Plots["Title"] = "Invariant Mass of Scalar H Resonance Derived from Truth Tops (Stack Plot)"
    Plots["xTitle"] = "Invariant Mass (GeV)"
    Plots["xMin"] = 0
    Plots["xStep"] = 100
    Plots["xScaling"] = 2.5
    Plots["Stack"] = True
    Plots["Filename"] = "Figure_1.1c"
    X = CombineTH1F(**Plots)
    X.SaveFigure()

def ResonanceDeltaRTops(x):
    Plots = PlotTemplate(x.NEvents, x.Luminosity)
    Plots["Histograms"] = []
    for k in x.TopsTypes:
        _Plots = {}
        _Plots["Title"] = k
        _Plots["xData"] = x.TopsTypes[k]
        _Plots["xBins"] = 1000
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    Plots["Title"] = "$\Delta$R Between Tops"
    Plots["xTitle"] = "$\Delta$R (a.u)"
    Plots["xMin"] = 0
    Plots["xStep"] = 0.25
    Plots["xScaling"] = 2.5 
    Plots["Filename"] = "Figure_1.1d"
    X = CombineTH1F(**Plots)
    X.SaveFigure()

def ResonanceTopKinematics(x):
    Plots = PlotTemplate(x.NEvents, x.Luminosity)
    Plots["Title"] = "Transverse Momenta of Tops Originating from Scalar H and Spectator Tops"
    Plots["xTitle"] = "Transverse Momenta (GeV)"
    Plots["Histograms"] = []
    Plots["xMin"] = 0
    Plots["xStep"] = 100
    Plots["xScaling"] = 2.5
    Plots["Filename"] = "Figure_1.1e"

    for i in x.TopsTypesPT:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = x.TopsTypesPT[i]
        _Plots["xBins"] = 500
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()
    

    Plots = PlotTemplate(x.NEvents, x.Luminosity)
    Plots["Title"] = "Energy of Tops Originating from Scalar H and Spectator Tops"
    Plots["xTitle"] = "Energy (GeV)"
    Plots["Histograms"] = []
    Plots["xMin"] = 0
    Plots["xStep"] = 100
    Plots["xScaling"] = 2.5
    Plots["Filename"] = "Figure_1.1f"

    for i in x.TopsTypesE:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = x.TopsTypesE[i]
        _Plots["xBins"] = 500
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()

    Plots = PlotTemplate(x.NEvents, x.Luminosity)
    Plots["Title"] = "Pseudorapidity of Tops Originating from Scalar H and Spectator Tops"
    Plots["xTitle"] = "Eta"
    Plots["xMin"] = -5
    Plots["xMax"] = 5
    Plots["xStep"] = 0.5
    Plots["Histograms"] = []
    Plots["Filename"] = "Figure_1.1g"

    for i in x.TopsTypesEta:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = x.TopsTypesEta[i]
        _Plots["xBins"] = 500
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()

    Plots = PlotTemplate(x.NEvents, x.Luminosity)
    Plots["Title"] = "Azimuth of Tops Originating from Scalar H and Spectator Tops"
    Plots["xTitle"] = "Phi"
    Plots["xMin"] = -3.5
    Plots["xMax"] = 3.5
    Plots["xStep"] = 0.5
    Plots["Histograms"] = []
    Plots["Filename"] = "Figure_1.1h"
    
    for i in x.TopsTypesPhi:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = x.TopsTypesPhi[i]
        _Plots["xBins"] = 500
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()

