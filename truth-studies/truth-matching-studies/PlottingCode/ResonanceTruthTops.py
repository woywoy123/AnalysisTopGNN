from AnalysisG.Plotting import TH1F, CombineTH1F, TH2F

def PlotTemplate(x):
    Plots = {
                "Style" : "ATLAS",
                "NEvents" : x.NEvents, 
                "ATLASLumi" : x.Luminosity,
                "OutputDirectory" : "./Figures/" + x.__class__.__name__, 
                "yTitle" : "Entries (a.u.)",
                "yMin" : 0,
            }
    return Plots

def ResonanceDecayModes(x):
    Plots = PlotTemplate(x)
    Plots["Title"] = "Decay Mode of the Resonance" 
    Plots["xTitle"] = "Decay Mode of scalar H (a.u)"
    Plots["xTickLabels"] = [
            "Lep (" + str(x.ResDecayMode["L"]) + ")", 
            "Had (" + str(x.ResDecayMode["H"]) + ")",
            "Had-Had (" + str(x.ResDecayMode["HH"]) + ")",
            "Had-Lep (" + str(x.ResDecayMode["HL"]) + ")", 
            "Lep-Lep (" + str(x.ResDecayMode["LL"]) + ")"]

    Plots["xWeights"] = [
            x.ResDecayMode["L"], x.ResDecayMode["H"], 
            x.ResDecayMode["HH"], x.ResDecayMode["HL"], x.ResDecayMode["LL"]]
    Plots["xStep"] = 1
    Plots["xBinCentering"] = True 
    Plots["Filename"] = "Figure_1.1a"
    F = TH1F(**Plots)
    F.SaveFigure()
    
    Plots = PlotTemplate(x)
    Plots["Title"] = "Decay Mode of all Tops" 
    Plots["xTitle"] = "Decay Mode of Tops (a.u)"
    Plots["xTickLabels"] = [
            "Res-Lep (" +  str(x.TopDecayMode["Res-L"] ) + ")", 
            "Res-Had (" +  str(x.TopDecayMode["Res-H"] ) + ")", 
            "Spec-Lep (" + str(x.TopDecayMode["Spec-L"]) + ")", 
            "Spec-Had (" + str(x.TopDecayMode["Spec-H"]) + ")"]

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
    Plots = PlotTemplate(x)
    Plots["Histograms"] = []
    for k in x.ResDecayMode:
        _Plots = {}
        dec = ""
        if k == "HH": dec = "Hadronic"
        if k == "HL": dec = "Hadronic-Leptonic"
        if k == "LL": dec = "Leptonic"
        if dec == "": continue 
        _Plots["Title"] = dec
        _Plots["xData"] = x.ResDecayMode[k]
        _Plots["xBins"] = 100
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    Plots["Title"] = "Invariant Mass of Scalar H Resonance Derived \n from Truth Tops (Stack Plot)"
    Plots["xTitle"] = "Invariant Mass (GeV)"
    Plots["xMin"] = 0
    Plots["xStep"] = 250
    Plots["Stack"] = True
    Plots["Filename"] = "Figure_1.1c"
    X = CombineTH1F(**Plots)
    X.SaveFigure()

def ResonanceDeltaRTops(x):
    Plots = PlotTemplate(x)
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
    Plots["xBins"] = 100
    Plots["xMax"] = 4
    Plots["Filename"] = "Figure_1.1d"
    X = CombineTH1F(**Plots)
    X.SaveFigure()

def ResonanceTopKinematics(x):
    Plots = PlotTemplate(x)
    Plots["Title"] = "Transverse Momenta of Tops Originating from \n Scalar H and Spectator Tops"
    Plots["xTitle"] = "Transverse Momenta (GeV)"
    Plots["Histograms"] = []
    Plots["xMin"] = 0
    Plots["xStep"] = 100
    Plots["xMax"] = 1200
    Plots["Filename"] = "Figure_1.1e"

    for i in x.TopsTypesPT:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = x.TopsTypesPT[i]
        _Plots["xBins"] = 500
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()
    

    Plots = PlotTemplate(x)
    Plots["Title"] = "Energy of Tops Originating from Scalar H and Spectator Tops"
    Plots["xTitle"] = "Energy (GeV)"
    Plots["Histograms"] = []
    Plots["xMin"] = 0
    Plots["xStep"] = 100
    Plots["xMax"] = 2000
    Plots["Filename"] = "Figure_1.1f"

    for i in x.TopsTypesE:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = x.TopsTypesE[i]
        _Plots["xBins"] = 500
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()

    Plots = PlotTemplate(x)
    Plots["Title"] = "Pseudorapidity of Tops Originating from Scalar H and Spectator Tops"
    Plots["xTitle"] = "Eta"
    Plots["xMin"] = -5
    Plots["xMax"] = 5
    Plots["xStep"] = 0.5
    Plots["xBins"] = 500
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

    Plots = PlotTemplate(x)
    Plots["Title"] = "Azimuth of Tops Originating from Scalar H and Spectator Tops"
    Plots["xTitle"] = "Phi"
    Plots["xMin"] = -3.5
    Plots["xMax"] = 3.5
    Plots["xStep"] = 0.5
    Plots["xBins"] = 500
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

    Plots = PlotTemplate(x)
    Plots["Title"] = "Transverse Momenta of Truth Tops (Spectator and Signal) \n as a Function of Energy"
    Plots["xBins"] = 500
    Plots["yBins"] = 500
    Plots["xMin"] = 0
    Plots["yMin"] = 0
    Plots["xMax"] = 2000
    Plots["yMax"] = 2000 
    Plots["xTitle"] = "Energy (GeV)"
    Plots["yTitle"] = "Transverse Momenta (GeV)" 
    Plots["Filename"] = "Figure_1.1i"
    Plots["xData"] = x.TopsTypesE["Res"] + x.TopsTypesE["Spec"]
    Plots["yData"] = x.TopsTypesPT["Res"] + x.TopsTypesPT["Spec"]
    t = TH2F(**Plots)
    t.SaveFigure()

    Plots = PlotTemplate(x)
    Plots["Title"] = "Transverse Momenta of Truth Tops (Spectator and Signal) \n as a Function of Pseudo-Rapidity"
    Plots["xBins"] = 500
    Plots["yBins"] = 500
    Plots["xMin"] = -5
    Plots["yMin"] = 0
    Plots["xMax"] = 5
    Plots["yMax"] = 2000 
    Plots["xTitle"] = "Pseudo Rapidity"
    Plots["yTitle"] = "Transverse Momenta (GeV)" 
    Plots["Filename"] = "Figure_1.1j"
    Plots["xData"] = x.TopsTypesEta["Res"] + x.TopsTypesEta["Spec"]
    Plots["yData"] = x.TopsTypesPT["Res"] + x.TopsTypesPT["Spec"]
    t = TH2F(**Plots)
    t.SaveFigure()


