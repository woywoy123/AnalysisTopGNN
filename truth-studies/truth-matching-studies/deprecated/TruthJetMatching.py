from AnalysisTopGNN.Plotting import TH1F, CombineTH1F, TH2F
from copy import copy

PDGID = { 1 : "d"        ,  2 : "u"             ,  3 : "s", 
          4 : "c"        ,  5 : "b"             , 11 : "e", 
         12 : "$\\nu_e$" , 13 : "$\mu$"         , 14 : "$\\nu_{\mu}$", 
         15 : "$\\tau$"  , 16 : "$\\nu_{\\tau}$", 21 : "g", 
         22 : "$\\gamma$"}

CounterPDGID = {"d"            : 0, "u"       : 0, "s"              : 0, "c"    : 0, 
                "b"            : 0, "e"       : 0, "$\\nu_e$"       : 0, "$\mu$": 0, 
                "$\\nu_{\mu}$" : 0, "$\\tau$" : 0, "$\\nu_{\\tau}$" : 0, "g"    : 0, 
                "$\\gamma$"    : 0}
 
_leptons = [11, 12, 13, 14, 15, 16]
_lepton_names = [PDGID[l] for l in _leptons]

def PlotTemplate(nevents, lumi):
    Plots = {
                "yTitle" : "Entries (a.u.)",
                "xMin" : 0, 
                "yMin" : 0, 
                "xMax" : None,
                "xBins" : None,
                "OutputDirectory" : "./Figures/TruthJet", 
                "Style" : "ATLAS",
                "ATLASLumi" : lumi,
                "NEvents" : nevents
            }
    return Plots


def TruthJetPartons(Ana):
    TopTruthJetPartons = copy(CounterPDGID)
    PTFraction = { i : [] for i in CounterPDGID}
    DeltaRPartonTJ = { i : [] for i in CounterPDGID}
    TruthJetPT = { "Top" : [], "Background" : [] }
    NumPartons = { "Top" : [], "Background" : [] }

    nevents = 0
    lumi = 0
    for ev in Ana:
        event = ev.Trees["nominal"]
        nevents += 1
        lumi += event.Lumi
        
        topTJ = [l for t in event.Tops for l in t.TruthJets]
        for tj in event.TruthJets:
            pt = tj.pt
            for p in tj.Parton:
                TopTruthJetPartons[PDGID[abs(p.pdgid)]] += 1
                PTFraction[PDGID[abs(p.pdgid)]].append(p.pt/pt)
                DeltaRPartonTJ[PDGID[abs(p.pdgid)]].append(tj.DeltaR(p))
            
            if tj in topTJ:
                TruthJetPT["Top"].append(tj.pt/1000)
                NumPartons["Top"].append(len(tj.Parton))
            else:
                TruthJetPT["Background"].append(tj.pt/1000)
                NumPartons["Background"].append(len(tj.Parton))

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Parton Contributions of Truth Jets (GhostParton)"
    Plots["xTitle"] = "Parton Symbol"
    Plots["xStep"] = 1
    Plots["Filename"] = "Figure_3.1a"
    Plots["xData"] = [i for i  in range(len(TopTruthJetPartons))]
    Plots["xWeights"] = [i for i in TopTruthJetPartons.values()]
    Plots["xTickLabels"] = [i for i in TopTruthJetPartons]
    Plots["xBinCentering"] = True
    x = TH1F(**Plots)
    x.SaveFigure()

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Fractional PT Contribution to Truth Jet (Stacked)"
    Plots["xTitle"] = "Transverse Momenta ($PT_{parton}$/$PT_{tj}$)"
    Plots["xStep"] = 1
    Plots["Filename"] = "Figure_3.1b"
    Plots["Histograms"] = []
    Plots["Stack"] = True
    Plots["Logarithmic"] = True
    for i in PTFraction:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = PTFraction[i]
        Plots["Histograms"].append(TH1F(**_Plots))
    x = CombineTH1F(**Plots) 
    x.SaveFigure()

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "$\Delta$R Between Contributing Parton and Truth Jet (Stacked)"
    Plots["xTitle"] = "$\Delta$R Between Parton and Truth Jet"
    Plots["xStep"] = 0.05
    Plots["xMax"] = 0.5
    Plots["Filename"] = "Figure_3.1c"
    Plots["Histograms"] = []
    Plots["Stack"] = False
    Plots["Logarithmic"] = False
    for i in DeltaRPartonTJ:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = DeltaRPartonTJ[i]
        Plots["Histograms"].append(TH1F(**_Plots))
    x = CombineTH1F(**Plots) 
    x.SaveFigure()

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Transverse Momenta of Truth Jet Originating \n Matched to Truth Top vs Background (Stacked)"
    Plots["xTitle"] = "Transverse Momenta of Truth Jet (GeV)"
    Plots["xStep"] = 100
    Plots["Filename"] = "Figure_3.1d"
    Plots["Histograms"] = []
    Plots["Stack"] = True
    Plots["Logarithmic"] = True
    for i in TruthJetPT:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = TruthJetPT[i]
        Plots["Histograms"].append(TH1F(**_Plots))
    x = CombineTH1F(**Plots) 
    x.SaveFigure()

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Number of contributing partons"
    Plots["xTitle"] = "#"
    Plots["xStep"] = 1
    Plots["xBinCentering"] = True
    Plots["xMin"] = -1
    Plots["Filename"] = "Figure_3.1d.2"
    Plots["Histograms"] = []
    for i in NumPartons:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = NumPartons[i]
        Plots["Histograms"].append(TH1F(**_Plots))
    X = CombineTH1F(**Plots)
    X.SaveFigure()

def PartonToChildTruthJet(Ana):
    MissedChild = {i : 0 for i in CounterPDGID}
    MissedChildQuarks = {i : 0 for i in CounterPDGID if i not in _lepton_names and i != "$\\gamma$"}
    Nchildren = {i : 0 for i in CounterPDGID}

    nevents = 0
    lumi = 0
    for ev in Ana:
        event = ev.Trees["nominal"]
        nevents += 1
        lumi += event.Lumi
        
        ChildrenIndex = {}
        ChildrenTJIndex = {}
        for c in range(len(event.TopChildren)):
            ChildrenIndex[c] = event.TopChildren[c]
            ChildrenTJIndex[c] = []
            Nchildren[PDGID[abs(event.TopChildren[c].pdgid)]] += 1
        
        for c in event.TruthJetPartons.values():
            for tci in ChildrenIndex:
                tc = ChildrenIndex[tci]
                if tc in c.Parent:
                    ChildrenTJIndex[tci].append(c)
        
        for c in ChildrenTJIndex:
            cpart = ChildrenIndex[c]
            sym = PDGID[abs(cpart.pdgid)]
            c = ChildrenTJIndex[c]
            if len(c) == 0:
                MissedChild[sym] += 1
                if sym not in _lepton_names and sym != "$\\gamma$":
                    MissedChildQuarks[sym] += 1
                continue


    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Top Child Lost in Truth Jets Contributions"
    Plots["xTitle"] = "Symbol"
    Plots["Filename"] = "Figure_3.1e"
    Plots["xStep"] = 1
    Plots["yTitle"] = "Percentage of lost children (%) by category"
    Plots["xData"] = [i for i in range(len(MissedChild))]
    Plots["xTickLabels"] = [i for i in MissedChild]
    Plots["xWeights"] = [float(MissedChild[i]/Nchildren[i])*100 if Nchildren[i] > 0 else 1 for i in MissedChild]
    Plots["xBinCentering"] = True
    x = TH1F(**Plots) 
    x.SaveFigure()

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Top Child Lost in Truth Jets Contributions (excl. leptons and photons)"
    Plots["xTitle"] = "Symbol"
    Plots["Filename"] = "Figure_3.1e.2"
    Plots["xStep"] = 1
    Plots["yTitle"] = "Percentage of lost children (%) by category"
    Plots["xData"] = [i for i in range(len(MissedChildQuarks))]
    Plots["xTickLabels"] = [i for i in MissedChildQuarks]
    Plots["xWeights"] = [float(MissedChildQuarks[i]/Nchildren[i])*100 if Nchildren[i] > 0 else 1 for i in MissedChildQuarks]
    Plots["xBinCentering"] = True
    x = TH1F(**Plots) 
    x.SaveFigure()

def ReconstructedTopMassTruthJet(Ana):
    TopMassPartons = {"Had" : [], "Lep" : []} 
    TopMassTruthJet = {"Had" : [], "Lep" : []} 
    ResonanceMass = {"Had-Had" : [], "Had-Lep" : [], "Lep-Lep" : []}

    nevents = 0
    lumi = 0

    resLost = 0
    resTopsLost = 0
    n_resTops = 0

    specTopsLost = 0
    n_specTops = 0

    hadTopsLost = 0
    n_hadTops = 0

    lepTopsLost = 0
    n_lepTops = 0
    
    TopsLost = 0
    ntops = 0

    for ev in Ana:
        event = ev.Trees["nominal"]
        nevents += 1
        lumi += event.Lumi

        stringR = {"Had" : [], "Lep" : []}
        for t in event.Tops:

            lp = "Lep" if sum([1 for c in t.Children if abs(c.pdgid) in _leptons]) > 0 else "Had"
           
            topTJ = [x for x in t.TruthJets]
            topTJ += [c for c in t.Children if abs(c.pdgid) in _leptons]

            topTJ = sum(topTJ)
           
            n_resTops += 1 if t.FromRes else 0
            n_specTops += 0 if t.FromRes else 1
            n_hadTops += 1 if lp == "Had" else 0
            n_lepTops += 1 if lp == "Lep" else 0
            
            ntops += 1
            if topTJ == 0:
                TopsLost += 1
                resTopsLost += 1 if t.FromRes else 0 
                specTopsLost += 0 if t.FromRes else 1
                hadTopsLost += 1 if lp == "Had" else 0
                lepTopsLost += 1 if lp == "Lep" else 0
                continue
            
            TopMassTruthJet[lp].append(topTJ.Mass)
            if t.FromRes == 1:
                stringR[lp].append(topTJ)
 
        res = sum([t for l in stringR for t in stringR[l]])
        if len([t for l in stringR for t in stringR[l]]) < 2:
            resLost += 1
            continue
        ResonanceMass["-".join([k for k in stringR for p in stringR[k]])] += [res.Mass]


    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Reconstructed Invariant Top Mass from Truth Jets \n (For Leptonic the Neutrinos are Included)"
    Plots["xTitle"] = "Invariant Mass (GeV)"
    Plots["xBins"] = 100
    Plots["xMin"] = 50
    Plots["xMax"] = 350
    Plots["Filename"] = "Figure_3.1f"
    Plots["Histograms"] = []
    for i in TopMassTruthJet:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = TopMassTruthJet[i]
        Plots["Histograms"].append(TH1F(**_Plots))
    x = CombineTH1F(**Plots) 
    x.SaveFigure()

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Reconstructed Invariant Scalar H Mass from Truth Jets\n (For Leptonic the Neutrinos are Included)"
    Plots["xTitle"] = "Invariant Mass (GeV)"
    Plots["xBins"] = 100
    Plots["xMin"] = 300
    Plots["xMax"] = 1700
    Plots["Filename"] = "Figure_3.1g"
    Plots["Histograms"] = []
    Plots["Stack"] = True
    for i in ResonanceMass:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = ResonanceMass[i]
        Plots["Histograms"].append(TH1F(**_Plots))
    x = CombineTH1F(**Plots) 
    x.SaveFigure()

    print("(Max Efficiency - Resonance Reconstruction) - " +  str(round(float(1 - float(resLost)/nevents)*100, 2)) + "%")
    print("(Max Efficiency - Resonance Tops) - " + str(round(float(1 - float(resTopsLost)/n_resTops)*100, 2)) + "%")
    print("(Max Efficiency - Spectator Tops) - " + str(round(float(1 - float(specTopsLost)/n_specTops)*100, 2)) + "%")
    print("(Max Efficiency - Hadronic Tops) - " + str(round(float(1 - float(hadTopsLost)/n_hadTops)*100, 2)) + "%")
    print("(Max Efficiency - Leptonic Tops) - " + str(round(float(1 - float(lepTopsLost)/n_lepTops)*100, 2)) + "%")
    print("(Max Efficiency - Tops) - " + str(round(float(1 - float(TopsLost)/ntops)*100, 2)) + "%")
    print("(Cross Section) - Resonance) - " + str(float((nevents - resLost)/lumi)*0.000001) + "fb")

    return {"ResEff"  : float(1 - float(resLost)/nevents)*100, 
            "ResTop"  : float(1 - float(resTopsLost)/n_resTops)*100, 
            "SpecTop" : float(1 - float(specTopsLost)/n_specTops)*100, 
            "Tops"    : float(1 - float(TopsLost)/ntops)*100, 
            "x-sec"   : float((nevents - resLost)/lumi)*0.000001}

    

def DeltaRTruthJets(Ana):
    CounterMerged = {"Non-Merged" : 0, "Merged" : 0, "Spec-Merged" : 0, "Spec-Non-Merged" : 0, "Res-Merged" : 0, "Res-Non-Merged" : 0} 
    DeltaRMutualTop = {"Signal" : [], "Spectator" : []}
    DeltaRNonMutualTop = {"Sig-Sig" : [], "Spec-Spec" : [], "Sig-Spec" : [], "Spec-Sig" : []}

    ntops = 0
    nevents = 0
    lumi = 0
    for ev in Ana:
        event = ev.Trees["nominal"]
        nevents += 1
        lumi += event.Lumi
        ntops += len(event.Tops) 
        
        checkedtops = []
        for t in event.Tops:
            
            # Check if any of the truth jets are merged (more than one top) if so, skip top
            merged = True if len([1 for tj in t.TruthJets if len(tj.index) > 1]) > 0 else False
            if merged:
                CounterMerged["Merged"] += 1
                CounterMerged["Res-Merged" if t.FromRes else "Spec-Merged"] += 1
                continue 
            CounterMerged["Non-Merged"] += 1 
            CounterMerged["Res-Non-Merged" if t.FromRes else "Spec-Non-Merged"] += 1

            checked = []
            for tj in t.TruthJets:
                for tj2 in t.TruthJets:
                    if tj2 == tj or tj2 in checked:
                        continue
                    DeltaRMutualTop["Signal" if t.FromRes else "Spectator"].append(tj.DeltaR(tj2))
                checked.append(tj)
            
            for t2 in event.Tops:
                if t2 == t or t2 in checkedtops:
                    continue

                stn = "Sig" if t.FromRes else "Spec"
                stn += "-"
                stn += "Sig" if t2.FromRes else "Spec"

                DeltaRNonMutualTop[stn] += [tj1.DeltaR(tj2) for tj1 in t.TruthJets for tj2 in t2.TruthJets]
            checkedtops.append(t) 
            
    DeltaRNonMutualTop["Sig-Spec"] += DeltaRNonMutualTop["Spec-Sig"] 
    del DeltaRNonMutualTop["Spec-Sig"]

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Counter of Merged and non-Merged Truth Jets\n Segmented into Spectator and Signal Tops"
    Plots["xData"] = [i for i in range(len(CounterMerged))]
    Plots["xWeights"] = [float(i/ntops)*100 for i in CounterMerged.values()]
    Plots["xTickLabels"] = [i for i in CounterMerged]
    Plots["xBinCentering"] = True 
    Plots["xStep"] = 1
    Plots["Filename"] = "Figure_3.1h"
    Plots["yTitle"] = "Percentage of Sampled Events (%)"
    x = TH1F(**Plots)
    x.SaveFigure() 

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "$\Delta$R Between Adjacent Truth Jets Originating from Same \n Signal and Spectator Tops (Considering only non-Merged Truth Jets)"
    Plots["Histograms"] = []
    Plots["xStep"] = 0.4
    Plots["xMin"] = 0
    Plots["xTitle"] = "$\Delta$Delta"
    Plots["Filename"] = "Figure_3.1i"
    
    for i in DeltaRMutualTop:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = DeltaRMutualTop[i]
        Plots["Histograms"].append(TH1F(**_Plots))
    x = CombineTH1F(**Plots) 
    x.SaveFigure()


    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "$\Delta$R Between Adjacent Truth Jets Originating from Different \n Truth Tops (Considering only non-Merged Truth Jets)"
    Plots["Histograms"] = []
    Plots["xStep"] = 0.4
    Plots["xMin"] = 0
    Plots["xTitle"] = "$\Delta$Delta"
    Plots["Filename"] = "Figure_3.1j"
    
    for i in DeltaRNonMutualTop:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = DeltaRNonMutualTop[i]
        Plots["Histograms"].append(TH1F(**_Plots))
    x = CombineTH1F(**Plots) 
    x.SaveFigure()
