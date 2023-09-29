from AnalysisG.Plotting import TH1F, CombineTH1F, TH2F

def PlotTemplate(x):
    Plots = {
                "yTitle" : "Entries (a.u.)",
                "xMin" : 0, 
                "yMin" : 0, 
                "xMax" : None,
                "xBins" : None,
                "OutputDirectory" : "./Figures/" + x.__class__.__name__, 
                "Style" : "ATLAS",
                "ATLASLumi" : x.Luminosity,
                "NEvents" : x.NEvents
            }
    return Plots

def PlotTemplateTH2F(x):
    Plots = {
                "xMin" : 0, 
                "yMin" : 0, 
                "OutputDirectory" : "./Figures/" + x.__class__.__name__, 
                "Style" : "ATLAS",
                "ATLASLumi" : x.Luminosity,
                "NEvents" : x.NEvents
            }
    return Plots

def TopMassJets(inpt):
    hist = PlotTemplate(inpt)
    hist["Title"] = "Reconstructed Invariant Mass of Top From (Truth) Jets \n Partitioned into Decay Topology"
    hist["xTitle"] = "Invariant Mass (GeV)"
    hist["xStep"] = 20
    hist["xMax"] = 360
    hist["xBins"] = 360
    hist["IncludeOverflow"] = True
    hist["Filename"] = "Figure_4.1a"
    hist["Histograms"] = []

    cols = iter(["Blue", "Red"])
    for mode in inpt.TopMassJet:
        c = next(cols)
        hist_m = {}
        hist_m["Title"] = mode + "(Jets)"
        hist_m["xData"] = inpt.TopMassJet[mode] 
        hist_m["Color"] = c
        hist["Histograms"].append(TH1F(**hist_m))        
        
        hist_m = {}
        hist_m["Title"] = mode + "(Truth Jets)"
        hist_m["xData"] = inpt.TopMassTruthJet[mode] 
        hist_m["Color"] = c
        hist_m["Texture"] = "/" 
        hist["Histograms"].append(TH1F(**hist_m))        
 
    com = CombineTH1F(**hist)
    #com.SaveFigure() 


    hist = PlotTemplate(inpt)
    hist["Title"] = "Number of (Truth) Jets Contributing to a Top \n Partitioned into Decay Topology"
    hist["xTitle"] = "Number of (Truth) Jets"
    hist["xStep"] = 1
    hist["Filename"] = "Figure_4.1b"
    hist["xBinCentering"] = True
    hist["Histograms"] = []
    cols = iter(["Blue", "Red"])
    for mode in inpt.NJets:
        c = next(cols)
        hist_m = {}
        hist_m["Title"] = mode + "(Jets)"
        hist_m["xData"] = inpt.NJets[mode] 
        hist_m["Color"] = c
        hist["Histograms"].append(TH1F(**hist_m))        
        
        hist_m = {}
        hist_m["Title"] = mode + "(Truth Jets)"
        hist_m["xData"] = inpt.NTruthJets[mode] 
        hist_m["Color"] = c
        hist_m["Texture"] = "/"
        hist["Histograms"].append(TH1F(**hist_m))        
        
    com = CombineTH1F(**hist)
    #com.SaveFigure() 
    
    xdata = {}
    for mode in inpt.TopMassJet:
        mass, nj = inpt.TopMassJet[mode], inpt.NJets[mode]
        for n, m in zip(nj, mass):
            if str(n) + "-Jets (" + mode + ")" not in xdata: xdata[str(n) + "-Jets (" + mode + ")"] = []
            xdata[str(n) + "-Jets (" + mode + ")"].append(m) 
            
    hist = PlotTemplate(inpt)
    hist["Title"] = "Reconstructed Invariant Top Mass using Jets \n Partitioned by Number of Jets"
    hist["xTitle"] = "Invariant Mass (GeV)"
    hist["xStep"] = 20
    hist["xMax"] = 360
    hist["xBins"] = 180
    hist["Filename"] = "Figure_4.1c"
    hist["Stack"] = True
    hist["IncludeOverflow"] = True
    hist["Histograms"] = []
 
    for n in xdata:
        hist_m = {}
        hist_m["Title"] = n
        hist_m["xData"] = xdata[n] 
        hist["Histograms"].append(TH1F(**hist_m))        
        
    com = CombineTH1F(**hist)
    #com.SaveFigure() 


    hist = PlotTemplate(inpt)
    hist["Title"] = "Reconstructed Invariant Top Mass using Jets \n and Detector Based Leptons with Truth Neutrinos"
    hist["xTitle"] = "Invariant Mass (GeV)"
    hist["xStep"] = 20
    hist["xMax"] = 360
    hist["xBins"] = 180
    hist["IncludeOverflow"] = True
    hist["Filename"] = "Figure_4.1d"
    hist["Histograms"] = []
 
    for mode in inpt.TopMassJetDetectorLep:
        if mode == "Had": continue
        hist_m = {}
        hist_m["Title"] = mode + " (Jets + Detector Leptons)"
        hist_m["xData"] = inpt.TopMassJetDetectorLep[mode] 
        hist["Histograms"].append(TH1F(**hist_m))        
        
        hist_m = {}
        hist_m["Title"] = mode + " (Jets + Truth Children Leptons)"
        hist_m["xData"] = inpt.TopMassJet[mode] 
        hist["Histograms"].append(TH1F(**hist_m))        

    com = CombineTH1F(**hist)
    #com.SaveFigure() 

    masshad = inpt.TopMassJet["Had"]
    njethad = inpt.NJets["Had"]
    xdata = {}
    for nj, m in zip(njethad, masshad):
        if nj not in xdata: xdata[nj] = []
        xdata[nj].append(m)

    hist = PlotTemplate(inpt)
    hist["Title"] = "Reconstructed Invariant Top Mass from Jets \n via Hadronic Decay Topology"
    hist["xTitle"] = "Invariant Mass (GeV)"
    hist["xStep"] = 20
    hist["xMax"] = 360
    hist["xBins"] = 180
    hist["IncludeOverflow"] = True
    hist["Filename"] = "Figure_4.1e"
    hist["Histograms"] = []
 
    for mode in xdata:
        hist_m = {}
        hist_m["Title"] = str(mode) + "-Jets"
        hist_m["xData"] = xdata[mode] 
        hist["Histograms"].append(TH1F(**hist_m))        
        
    com = CombineTH1F(**hist)
    com.SaveFigure() 


    hist_2 = PlotTemplateTH2F(inpt)
    hist_2["Title"] = "Average $\Delta$ R Clustering of Truth Matched Particles \n With Respect to Invariant Mass (Hadronic)"
    hist_2["xTitle"] = "Invariant Mass (GeV)"
    hist_2["yTitle"] = "Average $\Delta$R"
    hist_2["xBins"] = 180
    hist_2["xMax"] = 360
    hist_2["yBins"] = 180
    hist_2["yMax"] = 4
    hist_2["Filename"] = "Figure_4.1f"
    hist_2["xData"] = inpt.TopMassJet["Had"]
    hist_2["yData"] = inpt.DeltaRJets["Had"]
    th = TH2F(**hist_2)
    th.SaveFigure()

    hist_2 = PlotTemplateTH2F(inpt)
    hist_2["Title"] = "Average $\Delta$ R Clustering of Truth Matched Particles \n With Respect to Invariant Mass (Leptonic)"
    hist_2["xTitle"] = "Invariant Mass (GeV)"
    hist_2["yTitle"] = "Average $\Delta$R"
    hist_2["xBins"] = 180
    hist_2["xMax"] = 360
    hist_2["yBins"] = 180
    hist_2["yMax"] = 4
    hist_2["Filename"] = "Figure_4.2f"
    hist_2["xData"] = inpt.TopMassJet["Lep"]
    hist_2["yData"] = inpt.DeltaRJets["Lep"]
    th = TH2F(**hist_2)
    th.SaveFigure()

    hist_2 = PlotTemplateTH2F(inpt)
    hist_2["Title"] = "Average $\Delta$ R Clustering of Truth Matched Particles \n With Respect to Invariant Mass (All)"
    hist_2["xTitle"] = "Invariant Mass (GeV)"
    hist_2["yTitle"] = "Average $\Delta$R"
    hist_2["xBins"] = 180
    hist_2["xMax"] = 360
    hist_2["yBins"] = 180
    hist_2["yMax"] = 4
    hist_2["Filename"] = "Figure_4.3f"
    hist_2["xData"] = inpt.TopMassJet["Lep"] + inpt.TopMassJet["Had"]
    hist_2["yData"] = inpt.DeltaRJets["Lep"] + inpt.DeltaRJets["Had"]
    th = TH2F(**hist_2)
    th.SaveFigure() 

def MergedTopsJets(inpt):
    
    hist = PlotTemplate(inpt)
    hist["Title"] = "Jet Parton Transverse Momentum of \n Top Merged Jets (Partitioned into PDGID)"
    hist["xTitle"] = "Transverse Momentum (GeV)" 
    hist["IncludeOverflow"] = True 
    hist["Logarithmic"] = True
    hist["xStep"] = 50
    hist["xMax"] = 300
    hist["yMin"] = 1
    hist["xBins"] = 250
    hist["Filename"] = "Figure_4.1a"
    hist["Histograms"] = []
 
    for sym in inpt.PartonPT:
        plt = {}
        plt["Title"] = str(sym)
        plt["xData"] = inpt.PartonPT[sym]
        hist["Histograms"].append(TH1F(**plt))
    com = CombineTH1F(**hist)
    com.SaveFigure()
    
    hist = PlotTemplate(inpt)
    hist["Title"] = "Top Merged Jet Parton Energy \n (Partitioned into PDGID)"
    hist["xTitle"] = "Energy (GeV)" 
    hist["IncludeOverflow"] = True 
    hist["Logarithmic"] = True
    hist["yMin"] = 1
    hist["xStep"] = 50
    hist["xMax"] = 500
    hist["xBins"] = 250
    hist["Filename"] = "Figure_4.2a"
    hist["Histograms"] = []
 
    for sym in inpt.PartonEnergy:
        plt = {}
        plt["Title"] = str(sym)
        plt["xData"] = inpt.PartonEnergy[sym]
        hist["Histograms"].append(TH1F(**plt))
    com = CombineTH1F(**hist)
    com.SaveFigure()

    hist = PlotTemplate(inpt)
    hist["Title"] = "$\Delta$R Between Jet Axis and Partons contained in \n Top Merged Jets (Partitioned into PDGID)"
    hist["xTitle"] = "$\Delta$R Between Jet Axis and Partons" 
    hist["IncludeOverflow"] = True 
    hist["xStep"] = 0.1
    hist["xMax"] = 1.0
    hist["xBins"] = 250
    hist["Filename"] = "Figure_4.3a"
    hist["Histograms"] = []
 
    for sym in inpt.PartonDr:
        plt = {}
        plt["Title"] = str(sym)
        plt["xData"] = inpt.PartonDr[sym]
        hist["Histograms"].append(TH1F(**plt))
    com = CombineTH1F(**hist)
    com.SaveFigure()

    hist2D = PlotTemplateTH2F(inpt)
    hist2D["Title"] = "$\Delta$R Between Jet Axis and Contributing Partons \n as a Function of Parton's Energy (Only Gluons)"
    hist2D["xTitle"] = "Parton Energy (GeV)"
    hist2D["yTitle"] = "$\Delta R$"
    hist2D["IncludeOverflow"] = True
    hist2D["yMax"] = 0.6
    hist2D["xMax"] = 500
    hist2D["xMin"] = 0
    hist2D["yBins"] = 250
    hist2D["xBins"] = 250
    hist2D["xStep"] = 100
    hist2D["yStep"] = 0.1
    hist2D["yData"] = [i for m in inpt.PartonDr for i in inpt.PartonDr[m] if m == "g"]
    hist2D["xData"] = [i for m in inpt.PartonEnergy for i in inpt.PartonEnergy[m] if m == "g"]
    hist2D["Filename"] = "Figure_4.4a"
    hist2D = TH2F(**hist2D)
    hist2D.SaveFigure()

    hist2D = PlotTemplateTH2F(inpt)
    hist2D["Title"] = "$\Delta$R Between Jet Axis and Contributing Partons \n as a Function of Parton's Energy (Without Gluons)"
    hist2D["xTitle"] = "Parton Energy (GeV)"
    hist2D["yTitle"] = "$\Delta R$"
    hist2D["IncludeOverflow"] = True
    hist2D["yMax"] = 0.6
    hist2D["xMax"] = 500
    hist2D["xMin"] = 0
    hist2D["yBins"] = 250
    hist2D["xBins"] = 250
    hist2D["xStep"] = 100
    hist2D["yStep"] = 0.1
    hist2D["yData"] = [i for m in inpt.PartonDr for i in inpt.PartonDr[m] if m != "g"]
    hist2D["xData"] = [i for m in inpt.PartonEnergy for i in inpt.PartonEnergy[m] if m != "g"]
    hist2D["Filename"] = "Figure_4.5a"
    hist2D = TH2F(**hist2D)
    hist2D.SaveFigure()

    hist = PlotTemplate(inpt)
    hist["Title"] = "Transverse Momentum of Truth Children Matched to \n Jet Contributing Parton (Partitioned into PDGID)"
    hist["xTitle"] = "Transverse Momentum (GeV)" 
    hist["IncludeOverflow"] = True 
    hist["xStep"] = 100
    hist["xMax"] = 800
    hist["xBins"] = 250
    hist["Filename"] = "Figure_4.1b"
    hist["Histograms"] = []
 
    for sym in inpt.ChildPartonPT:
        plt = {}
        plt["Title"] = str(sym)
        plt["xData"] = inpt.ChildPartonPT[sym]
        hist["Histograms"].append(TH1F(**plt))
    com = CombineTH1F(**hist)
    com.SaveFigure()

    hist = PlotTemplate(inpt)
    hist["Title"] = "Energy of Truth Children Matched to \n Jet Contributing Parton (Partitioned into PDGID)"
    hist["xTitle"] = "Energy (GeV)" 
    hist["IncludeOverflow"] = True 
    hist["xStep"] = 100
    hist["xMax"] = 800
    hist["xBins"] = 250
    hist["Filename"] = "Figure_4.2b"
    hist["Histograms"] = []
 
    for sym in inpt.ChildPartonEnergy:
        plt = {}
        plt["Title"] = str(sym)
        plt["xData"] = inpt.ChildPartonEnergy[sym]
        hist["Histograms"].append(TH1F(**plt))
    com = CombineTH1F(**hist)
    com.SaveFigure()

    hist = PlotTemplate(inpt)
    hist["Title"] = "$\Delta$R Between Parton and Truth Child (Partitioned into Parton PDGID)"
    hist["xTitle"] = "$\Delta$R Between Parton and Truth Child" 
    hist["IncludeOverflow"] = True 
    hist["Logarithmic"] = True
    hist["xStep"] = 0.1
    hist["yMin"] = 1
    hist["xMax"] = 1.0
    hist["xBins"] = 250
    hist["Filename"] = "Figure_4.3b"
    hist["Histograms"] = []
 
    for sym in inpt.ChildPartonDr:
        plt = {}
        plt["Title"] = str(sym)
        plt["xData"] = inpt.ChildPartonDr[sym]
        hist["Histograms"].append(TH1F(**plt))
    com = CombineTH1F(**hist)
    com.SaveFigure()

    hist = PlotTemplate(inpt)
    hist["Title"] = "$\Delta$R Between Jet Axis and Truth Child \n (Partitioned into Parton PDGID)"
    hist["xTitle"] = "$\Delta$R Between Jet Axis and Truth Child" 
    hist["IncludeOverflow"] = True 
    hist["Logarithmic"] = True
    hist["xStep"] = 0.2
    hist["xMax"] = 3.0
    hist["yMin"] = 1
    hist["xBins"] = 400
    hist["Filename"] = "Figure_4.4b"
    hist["Histograms"] = []
 
    for sym in inpt.dRChildPartonJetAxis:
        plt = {}
        plt["Title"] = str(sym)
        plt["xData"] = inpt.dRChildPartonJetAxis[sym]
        hist["Histograms"].append(TH1F(**plt))
    com = CombineTH1F(**hist)
    com.SaveFigure()

    hist2D = PlotTemplateTH2F(inpt)
    hist2D["Title"] = "$\Delta$R Between Contributing Parton and Truth Child as a \n Function of Child's Energy (Only Gluons)"
    hist2D["xTitle"] = "Child Energy (GeV)"
    hist2D["yTitle"] = "$\Delta R$ Between Parton and Truth Child"
    hist2D["yMax"] = 1.0
    hist2D["xMax"] = 1000
    hist2D["xMin"] = 0
    hist2D["yBins"] = 250
    hist2D["xBins"] = 250
    hist2D["xStep"] = 100
    hist2D["yStep"] = 0.1
    hist2D["yData"] = [i for m in inpt.ChildPartonDr for i in inpt.ChildPartonDr[m] if m == "g"]
    hist2D["xData"] = [i for m in inpt.ChildPartonEnergy for i in inpt.ChildPartonEnergy[m] if m == "g"]
    hist2D["Filename"] = "Figure_4.5b"
    hist2D = TH2F(**hist2D)
    hist2D.SaveFigure()
    
    hist2D = PlotTemplateTH2F(inpt)
    hist2D["Title"] = "$\Delta$R Between Contributing Parton and Truth Child as a \n Function of Child's Energy (Without Gluons)"
    hist2D["xTitle"] = "Child Energy (GeV)"
    hist2D["yTitle"] = "$\Delta R$ Between Parton and Truth Child"
    hist2D["yMax"] = 1.0
    hist2D["xMax"] = 600
    hist2D["IncludeOverflow"] = True
    hist2D["xMin"] = 0
    hist2D["yBins"] = 100
    hist2D["xBins"] = 100
    hist2D["xStep"] = 50
    hist2D["yStep"] = 0.1
    hist2D["yData"] = [i for m in inpt.ChildPartonDr for i in inpt.ChildPartonDr[m] if m != "g"]
    hist2D["xData"] = [i for m in inpt.ChildPartonEnergy for i in inpt.ChildPartonEnergy[m] if m != "g"]
    hist2D["Filename"] = "Figure_4.6b"
    hist2D = TH2F(**hist2D)
    hist2D.SaveFigure()

    hist = PlotTemplate(inpt)
    hist["Title"] = "Parton Type Contribution Frequency Found in Top Merged Jets"
    hist["xTitle"] = "Frequency of Parton Symbol in Jets"
    hist["IncludeOverflow"] = True 
    hist["xStep"] = 1
    hist["xMax"] = 20
    hist["xBins"] = 20
    hist["xBinCentering"] = True
    hist["Filename"] = "Figure_4.1c"
    hist["Histograms"] = []
 
    for sym in inpt.NumberOfConstituentsInJet:
        plt = {}
        plt["Title"] = str(sym)
        plt["xData"] = inpt.NumberOfConstituentsInJet[sym]
        hist["Histograms"].append(TH1F(**plt))
    com = CombineTH1F(**hist)
    com.SaveFigure()

    hist = PlotTemplate(inpt)
    hist["Title"] = "Reconstructed Invariant Top Mass using the Hadronic \n Decay Topology from Jets"
    hist["xTitle"] = "Invariant Mass (GeV)"
    hist["IncludeOverflow"] = True 
    hist["xStep"] = 20
    hist["xMax"] = 400
    hist["xBins"] = 400
    hist["Filename"] = "Figure_4.2c"
    hist["Histograms"] = []
 
    for sym in inpt.TopsJets:
        plt = {}
        plt["Title"] = str(sym) + "-Tops"
        plt["xData"] = inpt.TopsJets[sym]
        hist["Histograms"].append(TH1F(**plt))
    com = CombineTH1F(**hist)
    com.SaveFigure()

    hist = PlotTemplate(inpt)
    hist["Title"] = "Reconstructed Invariant Top Mass using the Hadronic \n Decay Topology from Jets \n (A possible bug where No Partons are matched to Truth Jets)"
    hist["xTitle"] = "Invariant Mass (GeV)"
    hist["IncludeOverflow"] = True 
    hist["xStep"] = 20
    hist["xMax"] = 400
    hist["xBins"] = 400
    hist["Filename"] = "Figure_4.3c"
    hist["Histograms"] = []
 
    for sym in inpt.TopsJetsNoPartons:
        plt = {}
        plt["Title"] = str(sym) + "-Tops"
        plt["xData"] = inpt.TopsJetsNoPartons[sym]
        hist["Histograms"].append(TH1F(**plt))
    com = CombineTH1F(**hist)
    com.SaveFigure()

    hist = PlotTemplate(inpt)
    hist["Title"] = "Fractional Contribution of a given Top's Parton to a Jet"
    hist["xTitle"] = "Fractional Energy Contribution of Partons from a Given Top in Jet"
    hist["IncludeOverflow"] = True 
    hist["xStep"] = 0.1
    hist["xMax"] = 1.1
    hist["xBins"] = 100
    hist["yMin"] = 1
    hist["Logarithmic"] = True
    hist["Filename"] = "Figure_4.4c"
    hist["Histograms"] = []
 
    for sym in inpt.TopsJetsMerged:
        plt = {}
        plt["Title"] = str(sym) + "-Tops"
        plt["xData"] = inpt.TopsJetsMerged[sym]
        hist["Histograms"].append(TH1F(**plt))
    com = CombineTH1F(**hist)
    com.SaveFigure()

    hist = PlotTemplate(inpt)
    hist["Title"] = "Reconstructed Invariant Top Mass using the Hadronic \n Decay Topology from Jets using different Energy Fraction Cuts"
    hist["xTitle"] = "Invariant Mass (GeV)"
    hist["IncludeOverflow"] = True 
    hist["xStep"] = 20
    hist["xMax"] = 400
    hist["xBins"] = 200
    hist["Alpha"] = 0.1
    hist["Filename"] = "Figure_4.5c"
    hist["Histograms"] = []
 
    for sym in inpt.TopsJetsCut:
        plt = {}
        plt["Title"] = str(sym) + "-Cut"
        plt["xData"] = inpt.TopsJetsCut[sym]
        hist["Histograms"].append(TH1F(**plt))
    com = CombineTH1F(**hist)
    com.SaveFigure()
