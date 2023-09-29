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

def ResonanceMassTruthJets(con):

    res_m = PlotTemplate(con)
    res_m["Histograms"] = []
    for mode in con.ResMassTruthJets:
        m_hist = PlotTemplate(con)
        m_hist["Title"] = mode
        m_hist["xData"] = con.ResMassTruthJets[mode]
        m_hist["xBins"] = 1000
        res_m["Histograms"] += [TH1F(**m_hist)]
    
    res_m["Title"] = "Reconstructed Resonance from Truth Jets (Truth Matched)"
    res_m["xMin"] = 0
    res_m["xMax"] = 1500
    res_m["xStep"] = 100
    res_m["xTitle"] = "Invariant Mass (GeV)"
    res_m["Filename"] = "Figure_3.1a"
    res = CombineTH1F(**res_m)
    res.SaveFigure()

    stat = PlotTemplate(con)
    stat["Title"] = "Status Codes of the Event Selection"
    stat["xWeights"] = [con.CutFlow[i] for i in con.CutFlow]
    stat["xTickLabels"] = [i.replace(" ", "").replace("->", "::") + "\n (" + str(con.CutFlow[i]) + ")" for i in con.CutFlow]
    stat["xStep"] = 1
    stat["Filename"] = "Figure_3.1b"
    stat["xBinCentering"] = True
    stat = TH1F(**stat)
    stat.SaveFigure()

    it = 1
    for mode in con.ResMassTruthJets:
        m_hist = PlotTemplate(con) 
        m_hist["Title"] = "Truth Jets"
        m_hist["xData"] = con.ResMassTruthJets[mode]
        m_hist["xBins"] = 1000
        hists = [TH1F(**m_hist)]
        
        m_hist = PlotTemplate(con) 
        m_hist["Title"] = "Truth Tops"
        m_hist["xData"] = con.ResMassTops[mode]
        m_hist["xBins"] = 1000
        hists += [TH1F(**m_hist)]


        m_hist = PlotTemplate(con) 
        m_hist["Title"] = "Resonance Mass Plot Compared to Truth Tops \n via Decay Mode: " + mode
        m_hist["Histograms"] = hists
        m_hist["xStep"] = 100
        m_hist["xMax"] = 1500 
        m_hist["Filename"] = "Figure_3." + str(it) + "c"
        cm = CombineTH1F(**m_hist)  
        cm.SaveFigure()
        it += 1

    m_hist = PlotTemplate(con) 
    m_hist["Title"] = "Number of Truth-Jets Contributions Per Decay Topology"
    m_hist["Histograms"] = []
    m_hist["xStep"] = 1
    m_hist["xBinCentering"] = True
    m_hist["Filename"] = "Figure_3.1d"
    m_hist["xTitle"] = "n-Truth Jets"

    for mode in con.ResMassNTruthJets:
        hist = PlotTemplate(con) 
        hist["Title"] = mode
        hist["xData"] = con.ResMassNTruthJets[mode]
        m_hist["Histograms"] += [TH1F(**hist)]
    cm = CombineTH1F(**m_hist)  
    cm.SaveFigure()

def ResonanceMassTruthJetsNoSelection(con):
   
    it = 1
    for mode in con.ResMassTruthJets:
        m_hist = PlotTemplate(con) 
        m_hist["Title"] = "Truth Jets"
        m_hist["xData"] = con.ResMassTruthJets[mode]
        m_hist["xBins"] = 1000
        hists = [TH1F(**m_hist)]
        
        m_hist = PlotTemplate(con) 
        m_hist["Title"] = "Truth Tops"
        m_hist["xData"] = con.ResMassTops[mode]
        m_hist["xBins"] = 1000
        hists += [TH1F(**m_hist)]

        m_hist = PlotTemplate(con) 
        m_hist["Title"] = "Resonance Mass Plot Compared to Truth Tops \n via Decay Mode: " + mode
        m_hist["Histograms"] = hists
        m_hist["xStep"] = 100
        m_hist["xMax"] = 1500 
        m_hist["xTitle"] = "Invariant Mass (GeV)"
        m_hist["Filename"] = "Figure_3." + str(it) + "e"
        cm = CombineTH1F(**m_hist)  
        cm.SaveFigure()
        it += 1

    m_hist = PlotTemplate(con) 
    m_hist["Title"] = "Resonance Invariant Mass Plot from Different Top contributions"
    m_hist["xStep"] = 100
    m_hist["xMax"] = 1500 
    m_hist["xTitle"] = "Invariant Mass (GeV)"
    m_hist["Filename"] = "Figure_3.1f"
    m_hist["Histograms"] = []

    for cont in con.ResMassNTopContributions:
        hist = PlotTemplate(con) 
        hist["Title"] = str(cont) + " - Tops"
        hist["xData"] = con.ResMassNTopContributions[cont]
        hist["xBins"] = 1000
        m_hist["Histograms"] += [TH1F(**hist)]
    cm = CombineTH1F(**m_hist)  
    cm.SaveFigure()
    
    
    m_hist = PlotTemplate(con) 
    m_hist["Title"] = "Top Contributions by Decay Topology"
    m_hist["xStep"] = 1
    m_hist["xTitle"] = "Number of Top Contributions"
    m_hist["xBinCentering"] = True
    m_hist["Histograms"] = []
    m_hist["Filename"] = "Figure_3.1g"

    for cont in con.ResNTopContributions:
        hist = PlotTemplate(con) 
        hist["Title"] = cont
        hist["xData"] = con.ResNTopContributions[cont]
        hist["xBins"] = 4
        m_hist["Histograms"] += [TH1F(**hist)]
    cm = CombineTH1F(**m_hist)  
    cm.SaveFigure()
    
    





