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

def ResonanceMassJets(inpt):

    res = PlotTemplate(inpt)
    res["Title"] = "Reconstructed Resonance Invariant Mass From Jets \n Partitioned into Decay Topology"
    res["xTitle"] = "Invariant Mass (GeV)"
    res["yTitle"] = "Percentage (%)"
    res["xStep"] = 100
    res["xMax"] = 2000
    res["Filename"] = "Figure_4.1a"
    res["Normalize"] = "%"
    res["Histograms"] = []
    
    for mode in inpt.ResMassJets:
        m_hist = PlotTemplate(inpt)
        m_hist["Title"] = mode + " (jets)"
        m_hist["xData"] = inpt.ResMassJets[mode]
        m_hist["xBins"] = 1000
        res["Histograms"].append(TH1F(**m_hist))

    com = CombineTH1F(**res)
    com.SaveFigure()

    it = 1 
    for mode in inpt.ResMassJets:
        res = PlotTemplate(inpt)
        res["Title"] = "Reconstructed Resonance Invariant Mass From Jets (" + mode + ")"
        res["xTitle"] = "Invariant Mass (GeV)"
        res["xStep"] = 100
        res["xMax"] = 2000
        res["Filename"] = "Figure_4." + str(it) + "b"
        res["Histograms"] = []

        m_hist = PlotTemplate(inpt)
        m_hist["Title"] = mode + " (jets)"
        m_hist["xData"] = inpt.ResMassJets[mode]
        m_hist["xBins"] = 1000
        res["Histograms"].append(TH1F(**m_hist))

        m_hist = PlotTemplate(inpt)
        m_hist["Title"] = mode + " (truth-jets)"
        m_hist["xData"] = inpt.ResMassTruthJets[mode]
        m_hist["xBins"] = 1000
        res["Histograms"].append(TH1F(**m_hist))

        m_hist = PlotTemplate(inpt)
        m_hist["Title"] = mode + " (tops)"
        m_hist["xData"] = inpt.ResMassTops[mode]
        m_hist["xBins"] = 1000
        res["Histograms"].append(TH1F(**m_hist))

        com = CombineTH1F(**res)
        com.SaveFigure()
        it += 1
    
    res = PlotTemplate(inpt)
    res["Title"] = "Number of Jets Contributing to Resonance \n Partitioned into Decay Topology"
    res["xTitle"] = "n-Jets"
    res["xStep"] = 1
    res["xBins"] = 12
    res["xMax"] = 12
    res["IncludeOverflow"] = True
    res["xBinCentering"] = True
    res["Filename"] = "Figure_4.1c"
    res["Histograms"] = []

    for mode in inpt.ResMassNJets:
        m_hist = PlotTemplate(inpt)
        m_hist["Title"] = mode
        m_hist["xData"] = inpt.ResMassNJets[mode]
        res["Histograms"].append(TH1F(**m_hist))
    com = CombineTH1F(**res)
    com.SaveFigure() 

    res = PlotTemplate(inpt)
    res["Title"] = "Reconstructed Resonance Invariant Mass From Jets \n Partitioned into n-Jet Contributions"
    res["xTitle"] = "Invariant Mass (GeV)"
    res["xStep"] = 100
    res["xBins"] = 1000
    res["xMax"] = 2000
    res["IncludeOverflow"] = True
    res["Filename"] = "Figure_4.2c"
    res["Histograms"] = []

    xdata = {}
    for mode in inpt.ResMassNJets:
        for njet, mass in zip(inpt.ResMassNJets[mode], inpt.ResMassJets[mode]):
            if njet not in xdata: xdata[njet] = []
            xdata[njet] += [mass]
    
    for mode in sorted(xdata):
        m_hist = PlotTemplate(inpt)
        m_hist["Title"] = str(mode) + "-jets"
        m_hist["xData"] = xdata[mode]
        res["Histograms"].append(TH1F(**m_hist))
    com = CombineTH1F(**res)
    com.SaveFigure() 

    res = PlotTemplate(inpt)
    res["Title"] = "Reconstructed Resonance Invariant Mass From Jets \n Partitioned into n-Top Contributions and Decay Topology"
    res["xTitle"] = "Invariant Mass (GeV)"
    res["xStep"] = 100
    res["xBins"] = 1000
    res["xMax"] = 2000
    res["IncludeOverflow"] = True
    res["Filename"] = "Figure_4.1d"
    res["Histograms"] = []

    for mode in inpt.ResMassNTops:
        m_hist = PlotTemplate(inpt)
        m_hist["Title"] = mode
        m_hist["xData"] = inpt.ResMassNTops[mode]
        res["Histograms"].append(TH1F(**m_hist))
    com = CombineTH1F(**res)
    com.SaveFigure() 

    res_2D = PlotTemplate(inpt)
    res_2D["Title"] = "Reconstructed Resonance Invariant Mass From Jets \n (*Ideal Cases)"
    res_2D["xTitle"] = "Invariant Mass (GeV)"
    res_2D["yTitle"] = "Cross Over Contamination (Decay Topology) (Top Contribution)"
    res_2D["xData"] = [m for i in inpt.ResMassNTops for m in inpt.ResMassNTops[i]]
    res_2D["xBins"] = 200  
    res_2D["xStep"] = 200
    res_2D["xMax"] = 2000

    res_2D["yData"] = [i for i, m in zip(range(len(inpt.ResMassNTops)), inpt.ResMassNTops) for _ in inpt.ResMassNTops[m]]
    res_2D["yBinCentering"] = True 
    res_2D["yTickLabels"] = list(inpt.ResMassNTops)
    res_2D["Filename"] = "Figure_4.2d"
    res2D = TH2F(**res_2D)
    res2D.SaveFigure()

