from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.IO import UnpickleObject, PickleObject
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F
import gc

def PlotTemplate(nevents, lumi):
    Plots = {
                "yTitle" : "Entries (a.u.)",
                "xMin" : 0, 
                "yMin" : 0, 
                "xMax" : None,
                "xBins" : None,
                "OutputDirectory" : "./Figures/TruthJets", 
                "Style" : "ATLAS",
                "ATLASLumi" : lumi,
                "NEvents" : nevents
            }
    return Plots


def TruthJetAll(Ana):
    def DeltaR(top):
        truthjet = [tj for tj in top.TruthJets]
        delR = []
        for tj in top.TruthJets:
            for j in truthjet:
                if j == tj:
                    continue
                delR.append(j.DeltaR(tj))
            truthjet.pop(truthjet.index(tj)) 
        return delR

    _leptons = [11, 12, 13, 14, 15, 16]

    nevents = 0
    lumi = 0
    nevents2 = 0
    lumi2 = 0

    nLep = []
    nTruthJets = []
    
    nTopTruthJets = []
    nTopLeptons = []
    nBackgroundTruthJets = []

    nTopTruthJets_ExlLep = []
    DeltaRTopTruthJets_ExlLep = []
    DeltaRTopTruthJetsLep = []

    DeltaR_TopTruthJet_Background = []
    DeltaR_TopTruthJetLep_Background = []

    DeltaR_NonMutualTopTruthJets = []

    LostTops = []
    NSharedTruthJets_Res_Res = []
    NSharedTruthJets_Res_Spec = []

    MassOfTops = []
    MassOfTops_Lep = []

    MassOfZPrime = []
    MassOfZPrime_Lep = [] 

    PT_Res_TruthJets = []
    PT_Spec_TruthJets = []


    for i in Ana:
        event = i.Trees["nominal"]
        tops = event.TopPostFSR

        nLep.append(len(event.Leptons))
        nTruthJets.append(len(event.TruthJets))

        truthjets = []
        for t in tops:
            if len(t.Leptons) > 0:
                nTopLeptons.append(len(t.Leptons)) 
            nTopTruthJets.append(len(t.TruthJets))
            truthjets += [tj for tj in t.TruthJets if tj not in truthjets]
        
        background = [tj for tj in event.TruthJets if tj not in truthjets]
        nBackgroundTruthJets.append(len(background))

        for t in tops:
            if len(t.Leptons) > 0:
                DeltaRTopTruthJetsLep += DeltaR(t)
                DeltaR_TopTruthJetLep_Background += [jt.DeltaR(jb) for jt in t.TruthJets for jb in background]
                continue
            DeltaRTopTruthJets_ExlLep += DeltaR(t) 
            DeltaR_TopTruthJet_Background += [jt.DeltaR(jb) for jt in t.TruthJets for jb in background]

        for t in tops:
            if len(t.Leptons) > 0:
                continue
            nTopTruthJets_ExlLep.append(len(t.TruthJets))
                
        checked = []
        for t1 in tops:
            trujet1 = t1.TruthJets
            for t2 in tops:
                if t1 == t2 or t1 in checked:
                    continue
                trujet2 = t2.TruthJets

                DeltaR_NonMutualTopTruthJets += [tj1.DeltaR(tj2) for tj1 in trujet1 for tj2 in trujet2 if tj1 != tj2]
            checked.append(t1) 
        LostTops += [ 1 if len(t.TruthJets) == 0 else 0 for t in tops]
        
        checked = []
        for t in tops:
            for t2 in tops:
                if t2 == t or t2 in checked:
                    continue
                n = len([1 for tj in t.TruthJets if tj in t2.TruthJets])
                 
                if t.FromRes == 1 and t2.FromRes == 1:
                    NSharedTruthJets_Res_Res.append(n)
                elif t.FromRes == 1 and t2.FromRes == 0:
                    NSharedTruthJets_Res_Spec.append(n)
            checked.append(t)
        
        lep = []
        had = []
        _lepS = False
        for t in tops:
            if len([c for c in t.Children if abs(c.pdgid) in _leptons]) > 0:
                particle = sum(t.Leptons + t.TruthJets)
                if particle == 0:
                    continue
                MassOfTops_Lep.append(particle.CalculateMass())
                if t.FromRes == 1:
                    _lepS = True
            else: 
                particle = sum(t.TruthJets)
                if particle == 0:
                    continue
                MassOfTops.append(particle.CalculateMass())
            
            if t.FromRes == 0:
                continue
            
            if _lepS:
                lep.append(particle)
            else:
                had.append(particle)
        
        Zprime = sum(lep + had).CalculateMass()
        if len(lep) > 0:
            MassOfZPrime_Lep.append(Zprime)
        else:
            MassOfZPrime.append(Zprime)

        for t in tops:
            if len([c for c in t.Children if abs(c.pdgid) in _leptons]) > 0:
                particle = sum(t.Leptons + t.TruthJets)
                if particle == 0:
                    continue
                MassOfTops_Lep.append(particle.CalculateMass())
                if t.FromRes == 1:
                    _lepS = True
            else: 
                particle = sum(t.TruthJets)
                if particle == 0:
                    continue
                MassOfTops.append(particle.CalculateMass())
        
        _Res_top = []
        _Spec_top = []
        for t in tops: 
            _lep = False
            if len([c for c in t.Children if abs(c.pdgid) in _leptons]) > 0:
                _lep = True

            if t.FromRes == 1 and _lep:
                break
            if t.FromRes == 1:
                _Res_top.append(t) 
            if t.FromRes == 0:
                _Spec_top.append(t)
        
        if len(_Res_top) == 2:
            PT_Res_TruthJets += [tj.pt/1000 for t in _Res_top for tj in t.TruthJets]
            PT_Spec_TruthJets += [tj.pt/1000 for t in _Spec_top for tj in t.TruthJets]
            nevents2 += 1
            lumi2 += event.Lumi

        nevents += 1
        lumi += event.Lumi

    PlotNDecayProducts(nevents, lumi, nLep, nTruthJets)
    nLep = []
    nTruthJets = []
    gc.collect()

    PlotNTruthJets(nevents, lumi, nTopTruthJets, nTopLeptons, nBackgroundTruthJets)
    nTopTruthJets = []
    nTopLeptons = []
    gc.collect()

    PlotNTruthJets_ExlLeptonic(nevents, lumi, nTopTruthJets_ExlLep, nBackgroundTruthJets)
    nBackgroundTruthJets = []
    nTopTruthJets_ExlLep = []
    gc.collect()

    PlotDeltaRTopsTruthJets(nevents, lumi, DeltaRTopTruthJets_ExlLep, DeltaRTopTruthJetsLep)
    PlotDeltaRNonMutualTopTruthJets(nevents, lumi, DeltaRTopTruthJets_ExlLep, DeltaRTopTruthJetsLep, DeltaR_NonMutualTopTruthJets)
    DeltaRTopTruthJets_ExlLep = []
    DeltaRTopTruthJetsLep = []
    DeltaR_NonMutualTopTruthJets = []
    gc.collect() 

    PlotDeltaRTopsTruthJetsBackground(nevents, lumi, DeltaR_TopTruthJet_Background, DeltaR_TopTruthJetLep_Background)
    DeltaR_TopTruthJet_Background = []
    DeltaR_TopTruthJetLep_Background = []
    gc.collect()

    PlotLostTops(nevents, lumi, LostTops)
    LostTops = []
    gc.collect()

    PlotSharedTruthJets(nevents, lumi, NSharedTruthJets_Res_Res, NSharedTruthJets_Res_Spec)
    NSharedTruthJets_Res_Res, NSharedTruthJets_Res_Spec = [], []
    gc.collect()

    PlotInvariantMassTop(nevents, lumi, MassOfTops, MassOfTops_Lep)
    MassOfTops, MassOfTops_Lep = [], []
    gc.collect()

    PlotInvariantMassZPrime(nevents, lumi, MassOfZPrime, MassOfZPrime_Lep)
    MassOfZPrime, MassOfZPrime_Lep = [], []
    gc.collect()

    PlotPTSpecRes(nevents2, lumi2, PT_Spec_TruthJets, PT_Res_TruthJets)
    PT_Spec_TruthJets, PT_Res_TruthJets = [], []

def PlotNDecayProducts(nevents, lumi, nLep, nTruthJets):
    Plots = PlotTemplate(nevents, lumi)
    Plots["xStep"] = 1
    Plots["xTitle"] = "Number of Truth-Jets/Leptons"
    
    Plots["Title"] = "Leptons"
    Plots["xData"] = nLep
    Leps = TH1F(**Plots)

    Plots["Title"] = "Truth Jets"
    Plots["xData"] = nTruthJets
    Had = TH1F(**Plots)
        
    Plots["xData"] = []
    Plots["Histograms"] = [Leps, Had]
    Plots["Title"] = "Number of Truth-Jets/Leptons Produced by Tops in Event"
    Plots["Stack"] = True
    Plots["xBinCentering"] = True 
    Plots["Logarithmic"] = True
    Plots["Filename"] = "Figure.3.1a"
    com = CombineTH1F(**Plots)
    com.SaveFigure()

def PlotNTruthJets(nevents, lumi, nTopTruthJets, nTopLeptons, nBackgroundTruthJets):
    Plots = PlotTemplate(nevents, lumi)
    Plots["xStep"] = 1
    Plots["xTitle"] = "Number of Truth-Jets/Leptons"
    
    Plots["Title"] = "Leptons"
    Plots["xData"] = nTopLeptons
    Leps = TH1F(**Plots)

    Plots["Title"] = "Top-Truth-Jets"
    Plots["xData"] = nTopTruthJets
    Had = TH1F(**Plots)

    Plots["Title"] = "Unmatched-Truth-Jets"
    Plots["xData"] = nBackgroundTruthJets
    BKG = TH1F(**Plots)
        
    Plots["xData"] = []
    Plots["Histograms"] = [Leps, Had, BKG]
    Plots["Title"] = "Number of Truth-Jets/Leptons in Event"
    Plots["Stack"] = True
    Plots["xBinCentering"] = True 
    Plots["Logarithmic"] = True
    Plots["Filename"] = "Figure.3.1b"
    com = CombineTH1F(**Plots)
    com.SaveFigure()

def PlotNTruthJets_ExlLeptonic(nevents, lumi, nTopTruthJets_ExlLep, nBackgroundTruthJets):
    Plots = PlotTemplate(nevents, lumi)
    Plots["xStep"] = 1
    Plots["xTitle"] = "Number of Truth-Jets"
    
    Plots["Title"] = "Top-Truth-Jets"
    Plots["xData"] = nTopTruthJets_ExlLep
    Had = TH1F(**Plots)

    Plots["Title"] = "Unmatched-Truth-Jets"
    Plots["xData"] = nBackgroundTruthJets
    BKG = TH1F(**Plots)
 
    Plots["xData"] = []
    Plots["Histograms"] = [Had, BKG]
    Plots["Title"] = "Number of Truth-Jets Produced by Tops in Event\n - Excluding the Leptonically Decaying Top"
    Plots["Stack"] = True
    Plots["xBinCentering"] = True 
    Plots["xMax"] = 24
    Plots["Filename"] = "Figure.3.1c"
    com = CombineTH1F(**Plots)
    com.SaveFigure()

def PlotDeltaRTopsTruthJets(nevents, lumi, DeltaRTruthJets, DeltaRTruthJets_Lep):
    Plots = PlotTemplate(nevents, lumi)
    Plots["xStep"] = 0.2
    Plots["xTitle"] = "$\Delta$R"
    
    Plots["Title"] = "Hadronic"
    Plots["xData"] = DeltaRTruthJets
    Had = TH1F(**Plots)

    Plots["Title"] = "Leptonic"
    Plots["xData"] = DeltaRTruthJets_Lep
    BKG = TH1F(**Plots)
 
    Plots["xData"] = []
    Plots["Histograms"] = [Had, BKG]
    Plots["Title"] = "$\Delta$R of Truth Jets from Common Top"
    Plots["Filename"] = "Figure.3.1d"
    Plots["Logarithmic"] = True
    com = CombineTH1F(**Plots)
    com.SaveFigure()

def PlotDeltaRTopsTruthJetsBackground(nevents, lumi, Hadronic, Leptonic):
    Plots = PlotTemplate(nevents, lumi)
    Plots["xStep"] = 0.2
    Plots["xTitle"] = "$\Delta$R"
    Plots["xScaling"] = 2
    
    Plots["Title"] = "Hadronic"
    Plots["xData"] = Hadronic
    Had = TH1F(**Plots)

    Plots["Title"] = "Leptonic"
    Plots["xData"] = Leptonic
    BKG = TH1F(**Plots)
 
    Plots["xData"] = []
    Plots["Histograms"] = [Had, BKG]
    Plots["Title"] = "$\Delta$R of Truth Jets from Tops and Unmatched Truth Jets"
    Plots["Filename"] = "Figure.3.1e"
    Plots["Logarithmic"] = True
    com = CombineTH1F(**Plots)
    com.SaveFigure()

def PlotDeltaRNonMutualTopTruthJets(nevents, lumi, Hadronic, Leptonic, NonMutual):
    Plots = PlotTemplate(nevents, lumi)
    Plots["xStep"] = 0.2
    Plots["xScaling"] = 2
    Plots["Alpha"] = 0.5
    Plots["xTitle"] = "$\Delta$R"
    
    Plots["Title"] = "Mutual-Truth-Jets (Hadronic)"
    Plots["xData"] = Hadronic
    Had = TH1F(**Plots)

    Plots["Title"] = "Mutual-Truth-Jets (Leptonic)"
    Plots["xData"] = Leptonic
    Lep = TH1F(**Plots)

    Plots["Title"] = "non-Mutual-Truth-Jets"
    Plots["xData"] = NonMutual
    BKG = TH1F(**Plots)
 
    Plots["xData"] = []
    Plots["Histograms"] = [BKG, Had, Lep]
    Plots["Title"] = "$\Delta$R of Truth Jets With and Without Mutual Top"
    Plots["Filename"] = "Figure.3.1f"
    Plots["Logarithmic"] = True
    com = CombineTH1F(**Plots)
    com.SaveFigure()

def PlotLostTops(nevents, lumi, LostTops):
    Plots = PlotTemplate(nevents, lumi)
    Plots["xStep"] = 1
    Plots["xData"] = [0, 1]
    Plots["xWeights"] = [len([i for i in LostTops if i == 0]), len([i for i in LostTops if i == 1])]
    Plots["xTickLabels"] = ["Recoverable", "Lost"]
    Plots["Filename"] = "Figure.3.1g"
    Plots["Title"] = "Number of Tops Without Matched Truth Jet"
    Plots["xBinCentering"] = True
    x = TH1F(**Plots)
    x.SaveFigure()

def PlotSharedTruthJets(nevents, lumi, Res_Res, Res_Spec):

    Plots = PlotTemplate(nevents, lumi)
    Plots["Alpha"] = 0.5
    Plots["xStep"] = 1
    Plots["xBinCentering"] = True
    Plots["xTitle"] = "n-Shared Truth Jets"
    
    Plots["Title"] = "Res-Res-Tops"
    Plots["xData"] = Res_Res
    Res = TH1F(**Plots)

    Plots["Title"] = "Res-Spec-Tops"
    Plots["xData"] = Res_Spec
    Spec = TH1F(**Plots)

    Plots["xData"] = []
    Plots["Histograms"] = [Spec, Res]
    Plots["Title"] = "Truth Jets Shared between Tops"
    Plots["Filename"] = "Figure.3.1h"
    Plots["Logarithmic"] = True
    com = CombineTH1F(**Plots)
    com.SaveFigure()

def PlotInvariantMassTop(nevents, lumi, Hadronic, Lepton):

    Plots = PlotTemplate(nevents, lumi)
    Plots["Alpha"] = 0.5
    Plots["xStep"] = 10
    Plots["xMax"] = 400
    Plots["xScaling"] = 3
    Plots["xTitle"] = "Invariant Mass (GeV)"
    
    Plots["Title"] = "Hadronic"
    Plots["xData"] = Hadronic
    H = TH1F(**Plots)

    Plots["Title"] = "Leptonic"
    Plots["xData"] = Lepton
    L = TH1F(**Plots)

    Plots["xData"] = []
    Plots["Histograms"] = [H, L]
    Plots["Title"] = "Reconstructed Invariant Mass of Top Quark from Truth-Jets"
    Plots["Filename"] = "Figure.3.1i"
    com = CombineTH1F(**Plots)
    com.SaveFigure()

def PlotInvariantMassZPrime(nevents, lumi, Hadronic, Lepton):

    Plots = PlotTemplate(nevents, lumi)
    Plots["Alpha"] = 0.5
    Plots["xStep"] = 50
    Plots["xScaling"] = 3
    Plots["xMax"] = 2000
    Plots["xTitle"] = "Invariant Mass (GeV)"
    
    Plots["Title"] = "Hadronic"
    Plots["xData"] = Hadronic
    H = TH1F(**Plots)

    Plots["Title"] = "Leptonic"
    Plots["xData"] = Lepton
    L = TH1F(**Plots)

    Plots["xData"] = []
    Plots["Histograms"] = [L, H]
    Plots["Title"] = "Reconstructed Invariant Mass of Z-Prime Resonance"
    Plots["Filename"] = "Figure.3.1j"
    com = CombineTH1F(**Plots)
    com.SaveFigure()

def PlotPTSpecRes(nevents, lumi, PT_Spec, PT_Res):
    Plots = PlotTemplate(nevents, lumi)
    Plots["Alpha"] = 0.5
    Plots["xStep"] = 20
    Plots["xMax"] = 1100
    Plots["xScaling"] = 3
    Plots["xTitle"] = "Transverse Momenta of Truth Jet (GeV)"
    
    Plots["Title"] = "Resonance-TruthJets"
    Plots["xData"] = PT_Res
    H = TH1F(**Plots)

    Plots["Title"] = "Spectator-TruthJets"
    Plots["xData"] = PT_Spec
    L = TH1F(**Plots)

    Plots["xData"] = []
    Plots["Histograms"] = [H, L]
    Plots["Title"] = "Transverse Momenta of Truth-Jets for Events where Both Z' Tops Decay Hadronically"
    Plots["Filename"] = "Figure.3.1k"
    com = CombineTH1F(**Plots)
    com.SaveFigure()

   




