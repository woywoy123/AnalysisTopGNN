from AnalysisTopGNN.Plotting import TH1F, CombineTH1F
_leptons = [11, 12, 13, 14, 15, 16]

def PlotTemplate(nevents, lumi):
    Plots = {
                "Style" : "ATLAS",
                "NEvents" : nevents, 
                "ATLASLumi" : lumi,
                "OutputDirectory" : "./Figures/TruthTops", 
                "yTitle" : "Entries (a.u.)",
                "yMin" : 0,
            }
    return Plots

def ResonanceDecayModes(Ana):
    
    ResDecayMode = {"Had" : 0, "Lep" : 0, "Had-Had" : 0, "Had-Lep" : 0, "Lep-Lep" : 0}
    TopDecayMode = {"Spec-Had" : 0, "Spec-Lep" : 0, "Res-Had" : 0, "Res-Lep" : 0}
    
    lumi = 0
    nevents = 0
    for ev in Ana:
        event = ev.Trees["nominal"]
        nevents += 1
        lumi += event.Lumi
        
        _lep = False
        string = {"Had" : 0, "Lep" : 0}
        for t in event.Tops:
            
            # Check if the given top decays leptonically 
            lp = "Lep" if sum([1 for c in t.Children if abs(c.pdgid) in _leptons]) > 0 else "Had"
            res = "Spec" if t.FromRes == 0 else "Res"
            
            TopDecayMode[res + "-" + lp] += 1
            if res == "Res" and lp == "Lep":
                _lep = True

            if res == "Res":
                string[lp] += 1

        ResDecayMode["Lep" if _lep else "Had"] += 1
        ResDecayMode["-".join([k for k in string for p in range(string[k])])] += 1

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Decay Mode of the Resonance" 
    Plots["xTitle"] = "Decay Mode of scalar H (a.u)"
    Plots["xTickLabels"] = ["Lep (" +   str(ResDecayMode["Lep"]    ) + ")", 
                            "Had (" +   str(ResDecayMode["Had"]    ) + ")",
                            "Had-Had (" + str(ResDecayMode["Had-Had"]) + ")",
                            "Had-Lep (" + str(ResDecayMode["Had-Lep"]) + ")", 
                            "Lep-Lep (" + str(ResDecayMode["Lep-Lep"]) + ")"]

    Plots["xData"] = [0, 1, 2, 3, 4]
    Plots["xWeights"] = [ResDecayMode["Lep"],    
                         ResDecayMode["Had"],    
                         ResDecayMode["Had-Had"], 
                         ResDecayMode["Had-Lep"], 
                         ResDecayMode["Lep-Lep"]]
    Plots["xMin"] = 0
    Plots["xStep"] = 1
    Plots["xBinCentering"] = True 
    Plots["Filename"] = "Figure_1.1a"
    F = TH1F(**Plots)
    F.SaveFigure()
    

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Decay Mode of all Tops" 
    Plots["xTitle"] = "Decay Mode of Tops (a.u)"
    Plots["xTickLabels"] = ["Res-Lep (" +  str(TopDecayMode["Res-Lep"] ) + ")", 
                            "Res-Had (" +  str(TopDecayMode["Res-Had"] ) + ")", 
                            "Spec-Lep (" + str(TopDecayMode["Spec-Lep"]) + ")", 
                            "Spec-Had (" + str(TopDecayMode["Spec-Had"]) + ")"]
    Plots["xData"] = [0, 1, 2, 3]
    Plots["xWeights"] = [TopDecayMode["Res-Lep"], TopDecayMode["Res-Had"],
                        TopDecayMode["Spec-Lep"], TopDecayMode["Spec-Had"]]

    Plots["xMin"] = 0
    Plots["xStep"] = 1
    Plots["xBinCentering"] = True 
    Plots["Filename"] = "Figure_1.1b"
    F = TH1F(**Plots)
    F.SaveFigure()

def ResonanceMassFromTops(Ana):
    
    lumi = 0
    nevents = 0
    ResDecayMode = {"Had-Had" : [], "Had-Lep" : [], "Lep-Lep" : []}

    for ev in Ana:
        event = ev.Trees["nominal"]
        nevents += 1
        lumi += event.Lumi
        
        string = {"Had" : 0, "Lep" : 0}
        part = []
        for t in event.Tops:
            if t.FromRes == 0:
                continue
            
            # Check if the given top decays leptonically 
            lp = "Lep" if sum([1 for c in t.Children if abs(c.pdgid) in _leptons]) > 0 else "Had"
            string[lp] += 1
            part.append(t)
        ResDecayMode["-".join([k for k in string for p in range(string[k])])].append(sum(part))
    
    Plots = PlotTemplate(nevents, lumi)
    Plots["Histograms"] = []
    for k in ResDecayMode:
        _Plots = {}
        _Plots["Title"] = k
        _Plots["xData"] = [p.CalculateMass() for p in ResDecayMode[k]]
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    Plots["Title"] = "Invariant Mass of Scalar H Resonance \n Derived from Truth Tops (Stack Plot)"
    Plots["xTitle"] = "Invariant Mass (GeV)"
    Plots["xMin"] = 0
    Plots["xStep"] = 20
    Plots["xScaling"] = 2.5
    Plots["Stack"] = True
    Plots["Filename"] = "Figure_1.1c"
    X = CombineTH1F(**Plots)
    X.SaveFigure()


def DeltaRTops(Ana):
    
    lumi = 0
    nevents = 0
    TopsTypes = {"Res-Spec" : [], "Res-Res" : [], "Spec-Spec" : []}
    
    for ev in Ana:
        event = ev.Trees["nominal"]
        nevents += 1
        lumi += event.Lumi

        fin = []
        for t1 in event.Tops:
            for t2 in event.Tops:
                if t1 == t2 or t2 in fin:
                    continue
                string = {"Res" : 0, "Spec" : 0}           
                string["Res" if t1.FromRes == 1 else "Spec"] += 1
                string["Res" if t2.FromRes == 1 else "Spec"] += 1
                TopsTypes["-".join([k for k in string for p in range(string[k])])].append(t1.DeltaR(t2))
            fin.append(t1)

    Plots = PlotTemplate(nevents, lumi)
    Plots["Histograms"] = []
    for k in TopsTypes:
        _Plots = {}
        _Plots["Title"] = k
        _Plots["xData"] = TopsTypes[k]
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    Plots["Title"] = "$\Delta$R Between Tops"
    Plots["xTitle"] = "$\Delta$R (a.u)"
    Plots["xMin"] = 0
    Plots["xStep"] = 0.25
    Plots["xScaling"] = 2.5 
    Plots["Filename"] = "Figure_1.1d"
    X = CombineTH1F(**Plots)
    X.SaveFigure()

def TopKinematics(Ana):

    lumi = 0
    nevents = 0
    TopsTypesPT = {"Res" : [], "Spec" : []}
    TopsTypesE = {"Res" : [], "Spec" : []}
    TopsTypesEta = {"Res" : [], "Spec" : []}
    TopsTypesPhi = {"Res" : [], "Spec" : []}

    for ev in Ana:
        event = ev.Trees["nominal"]
        nevents += 1
        lumi += event.Lumi

        for t in event.Tops:
            TopsTypesPT["Res" if t.FromRes == 1 else "Spec"] += [t.pt / 1000]
            TopsTypesE["Res" if t.FromRes == 1 else "Spec"] += [t.e / 1000]
            TopsTypesEta["Res" if t.FromRes == 1 else "Spec"] += [t.eta]
            TopsTypesPhi["Res" if t.FromRes == 1 else "Spec"] += [t.phi]

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Transverse Momenta of Tops Originating from Scalar H and Spectator Tops"
    Plots["xTitle"] = "Transverse Momenta (GeV)"
    Plots["Histograms"] = []
    Plots["xMin"] = 0
    Plots["xStep"] = 25
    Plots["xScaling"] = 2.5
    Plots["Filename"] = "Figure_1.1e"

    for i in TopsTypesPT:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = TopsTypesPT[i]
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()
    

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Energy of Tops Originating from Scalar H and Spectator Tops"
    Plots["xTitle"] = "Energy (GeV)"
    Plots["Histograms"] = []

    for i in TopsTypesE:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = TopsTypesE[i]
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    Plots["xMin"] = 0
    Plots["xStep"] = 100
    Plots["xScaling"] = 2.5
    Plots["Filename"] = "Figure_1.1f"

    X = CombineTH1F(**Plots)
    X.SaveFigure()

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Pseudorapidity of Tops Originating from Scalar H and Spectator Tops"
    Plots["xTitle"] = "Eta"
    Plots["xBins"] = 50
    Plots["xMin"] = -5
    Plots["xMax"] = 5
    Plots["Histograms"] = []

    for i in TopsTypesEta:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = TopsTypesEta[i]
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    Plots["Filename"] = "Figure_1.1g"

    X = CombineTH1F(**Plots)
    X.SaveFigure()

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Azimuth of Tops Originating from Scalar H and Spectator Tops"
    Plots["xTitle"] = "Phi"
    Plots["xBins"] = 70
    Plots["xMin"] = -3.5
    Plots["xMax"] = 3.5
    Plots["Histograms"] = []

    for i in TopsTypesPhi:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = TopsTypesPhi[i]
        Plots["Histograms"] += [TH1F(**_Plots)]
    
    Plots["Filename"] = "Figure_1.1h"

    X = CombineTH1F(**Plots)
    X.SaveFigure()

