# Produce the plotting of the events in the analysis (basically a sanity check) 
from Functions.Event.Event import EventGenerator
from Functions.Particles.Particles import Particle
from Functions.IO.IO import UnpickleObject, PickleObject
from Functions.Plotting.Histograms import TH2F, TH1F, SubfigureCanvas, CombineHistograms
from Functions.GNN.Graphs import GenerateDataLoader
from Functions.GNN.Optimizer import Optimizer
from Functions.GNN.Metrics import EvaluationMetrics

def TestTops():
   
    x = UnpickleObject("EventGenerator")
    x = x.Events 

    # Top mass containers 
    Top_Mass = []
    Top_Mass_From_Children = []
    Top_Mass_From_Children_init = []
    Top_Mass_From_Truth_Jets = []
    Top_Mass_From_Truth_Jets_init = []
    Top_Mass_From_Truth_Jets_NoAnomaly = []
    Top_Mass_From_Jets = []
    for i in x:
        ev = x[i]["nominal"]
        
        tops = ev.TruthTops
        for k in tops:
            k.CalculateMass()
            Top_Mass.append(k.Mass_GeV)
            
            k.CalculateMassFromChildren()
            Top_Mass_From_Children.append(k.Mass_GeV)
            Top_Mass_From_Children_init.append(k.Mass_init_GeV)
    
        for k in tops:

            # Calculation of top mass from truth jets + detector leptons 
            tmp = []
            for j in k.Decay:
                tmp += j.Decay
            k.Decay = tmp
            tmp = []
            for j in k.Decay_init:
                tmp += j.Decay_init
            k.Decay_init = tmp
            
            k.CalculateMassFromChildren()
            Top_Mass_From_Truth_Jets.append(k.Mass_GeV)
            Top_Mass_From_Truth_Jets_init.append(k.Mass_init_GeV)
        
            if ev.Anomaly_TruthMatch == False:
                Top_Mass_From_Truth_Jets_NoAnomaly.append(k.Mass_GeV)

            # Now we calculate from detector jets
            tmp = []
            for j in k.Decay:
                if j.Type == "truthjet":
                    tmp += j.Decay
                else:
                    tmp.append(j)
            k.Decay = tmp
            k.CalculateMassFromChildren()
            Top_Mass_From_Jets.append(k.Mass_GeV)

    # Tops from Truth information figures 
    s = SubfigureCanvas()
    s.Filename = "TopMasses"

    t = TH1F() 
    t.Title = "The Mass of Truth Top From 'truth_top_*'"
    t.xTitle = "Mass (GeV)"
    t.yTitle = "Entries"
    t.xBins = 200
    t.xData = Top_Mass
    t.CompileHistogram()
    s.AddObject(t)

    tc = TH1F()
    tc.Title = "The Predicted Truth Top Mass Derived From 'truth_top_child_*'"
    tc.xTitle = "Mass (GeV)"
    tc.yTitle = "Entries"
    tc.xBins = 200
    tc.xMin = 160
    tc.xData = Top_Mass_From_Children
    tc.CompileHistogram()
    s.AddObject(tc)   

    tc_init = TH1F()
    tc_init.Title = "The Predicted Truth Top Mass Derived From 'truth_top_child_init_*'"
    tc_init.xTitle = "Mass (GeV)"
    tc_init.yTitle = "Entries"
    tc_init.xMin = 160
    tc_init.xBins = 200
    tc_init.xData = Top_Mass_From_Children_init
    tc_init.CompileHistogram()
    s.AddObject(tc_init)
    
    s.SaveFigure()

    # Comparison Plot of the Truth Top Mass from children and truth jets
    s = SubfigureCanvas()
    s.Filename = "TopMassesDetector"
 
    tc = TH1F()
    tc.Title =  "The Predicted Truth Top Mass Derived From 'truth_top_child_*'"
    tc.xTitle = "Mass (GeV)"
    tc.yTitle = "Entries"
    tc.xMin = 160
    tc.xBins = 200
    tc.xData = Top_Mass_From_Children
    tc.CompileHistogram()
    s.AddObject(tc)   

    t = TH1F()
    t.Title = "The Predicted Truth Top Mass Derived From 'truth_jets_*' \n (with detector leptons) matched to 'truth_top_child_*'"
    t.xTitle = "Mass (GeV)"
    t.yTitle = "Entries"
    t.xMin = 160
    t.xBins = 200
    t.xData = Top_Mass_From_Truth_Jets
    t.CompileHistogram()
    s.AddObject(t)
    
    tc_init = TH1F()
    tc_init.Title = "The Predicted Truth Top Mass Derived From 'truth_jets_*' \n (with detector leptons) matched to 'truth_top_child_init*'"
    tc_init.xTitle = "Mass (GeV)"
    tc_init.yTitle = "Entries"
    tc_init.xMin = 160
    tc_init.xBins = 200
    tc_init.xData = Top_Mass_From_Truth_Jets_init
    tc_init.CompileHistogram()
    s.AddObject(tc_init)
    s.SaveFigure()


    # Comparison of Top mass from truthjets vs top_child information + No Anomalous Event matching 
    s = SubfigureCanvas()
    s.Filename = "TopMassesDetectorNoAnomalous"
 
    tc = TH1F()
    tc.Title =  "The Predicted Truth Top Mass Derived From 'truth_top_child_*'"
    tc.xTitle = "Mass (GeV)"
    tc.yTitle = "Entries"
    tc.xMin = 160
    tc.xBins = 200
    tc.xData = Top_Mass_From_Children
    tc.CompileHistogram()
    s.AddObject(tc)   

    t = TH1F()
    t.Title = "The Predicted Truth Top Mass Derived From 'truth_jets_*' \n (with detector leptons) matched to 'truth_top_child_*'"
    t.xTitle = "Mass (GeV)"
    t.yTitle = "Entries"
    t.xMin = 160
    t.xBins = 200
    t.xData = Top_Mass_From_Truth_Jets
    t.CompileHistogram()
    s.AddObject(t)
    
    tc_init = TH1F()
    tc_init.Title = "The Predicted Truth Top Mass Derived From 'truth_jets_*' \n (with detector leptons) matched to 'truth_top_child_*' (No Truth Jet Missmatch)"
    tc_init.xTitle = "Mass (GeV)"
    tc_init.yTitle = "Entries"
    tc_init.xMin = 160
    tc_init.xBins = 200
    tc_init.xData = Top_Mass_From_Truth_Jets_NoAnomaly
    tc_init.CompileHistogram()
    s.AddObject(tc_init)
    s.SaveFigure()

    # Comparison of Top mass from jets vs top_child information + No Anomalous Event matching 
    s = SubfigureCanvas()
    s.Filename = "TopMassesDetectorJet"
 
    tc = TH1F()
    tc.Title =  "The Predicted Truth Top Mass Derived From 'truth_top_child_*'"
    tc.xTitle = "Mass (GeV)"
    tc.yTitle = "Entries"
    tc.xMin = 160
    tc.xBins = 200
    tc.xData = Top_Mass_From_Children
    tc.CompileHistogram()
    s.AddObject(tc)   

    t = TH1F()
    t.Title = "The Predicted Truth Top Mass Derived From 'truth_jets_*'\n (with detector leptons) matched to 'truth_top_child_*'"
    t.xTitle = "Mass (GeV)"
    t.yTitle = "Entries"
    t.xMin = 160
    t.xBins = 200
    t.xData = Top_Mass_From_Truth_Jets
    t.CompileHistogram()
    s.AddObject(t)
    
    tc_init = TH1F()
    tc_init.Title = "The Predicted Truth Top Mass Derived From 'jets_*'\n (with detector leptons) matched to 'truth_top_child_*'"
    tc_init.xTitle = "Mass (GeV)"
    tc_init.yTitle = "Entries"
    tc_init.xMin = 160
    tc_init.xBins = 200
    tc_init.xData = Top_Mass_From_Jets
    tc_init.CompileHistogram()
    s.AddObject(tc_init)
    s.SaveFigure()

    return True

def TestResonance():
    x = UnpickleObject("EventGenerator")
    x = x.Events 

    # Top mass containers 
    Res_TruthTops = []
    Res_Child = []
    Res_Child_init = []
    Res_TruthJet = []
    Res_TruthJet_NoAnomaly = []
    Res_Jet = []
    for i in x:
        ev = x[i]["nominal"]
        
        tops = ev.TruthTops
        Z_ = Particle(True)
        Sigs = []
        for t in tops:
            # Signal Tops from Resonance 
            if t.FromRes == 0:
                continue
            Sigs.append(t)

        # Resonance Mass from Truth Tops 
        Z_.Decay = Sigs
        Z_.CalculateMassFromChildren()
        Res_TruthTops.append(Z_.Mass_GeV)
        
        Z_.Decay = []
        # Resonance Mass from Truth Children
        for t in Sigs:
            Z_.Decay += t.Decay
            Z_.Decay_init += t.Decay_init

        Z_.CalculateMassFromChildren()
        Res_Child.append(Z_.Mass_GeV)
        Res_Child_init.append(Z_.Mass_init_GeV)

        Z_.Decay = []
        Z_.Decay_init = []
        #Resonance Mass from Truth Jets
        for t in Sigs:
            for tc in t.Decay:
                Z_.Decay.append(tc)

        Z_.CalculateMassFromChildren()
        Res_TruthJet.append(Z_.Mass_GeV)
        
        Z_.Decay = []
        #Resonance Mass from Truth Jets Good Matching 
        if ev.Anomaly_TruthMatch == False: 
            for t in Sigs:
                for tc in t.Decay:
                    Z_.Decay.append(tc)
        
            Z_.CalculateMassFromChildren()
            Res_TruthJet_NoAnomaly.append(Z_.Mass_GeV)
 
        Z_.Decay = []  
        #Resonance Mass from Truth Jets
        for t in Sigs:
            for tc in t.Decay:
                if tc.Type == "truthjet":
                    Z_.Decay += tc.Decay
                else:
                    Z_.Decay.append(tc)

        Z_.CalculateMassFromChildren()
        Res_Jet.append(Z_.Mass_GeV)
 
    # Tops from Truth information figures 
    s = SubfigureCanvas()
    s.Filename = "ResonanceMassTruthParticles"

    t = TH1F() 
    t.Title = "The Mass of Resonance Using 'truth_top_*'"
    t.xTitle = "Mass (GeV)"
    t.yTitle = "Entries"
    t.xBins = 200
    t.xData = Res_TruthTops
    t.CompileHistogram()
    s.AddObject(t)

    tc = TH1F()
    tc.Title = "The Predicted Resonance Mass Derived From 'truth_top_child_*'"
    tc.xTitle = "Mass (GeV)"
    tc.yTitle = "Entries"
    tc.xBins = 200
    tc.xData = Res_Child
    tc.CompileHistogram()
    s.AddObject(tc)   

    tc_init = TH1F()
    tc_init.Title = "The Predicted Resonance Mass Derived From 'truth_top_child_init*'"
    tc_init.xTitle = "Mass (GeV)"
    tc_init.yTitle = "Entries"
    tc_init.xBins = 200
    tc_init.xData = Res_Child_init
    tc_init.CompileHistogram()
    s.AddObject(tc_init)
    
    s.SaveFigure()

    # Comparison Plot of the Truth Top Mass from children and truth jets
    s = SubfigureCanvas()
    s.Filename = "ResonanceMassTruthJets"
 
    t = TH1F() 
    t.Title = "The Mass of Resonance Using 'truth_top_*'"
    t.xTitle = "Mass (GeV)"
    t.yTitle = "Entries"
    t.xBins = 200
    t.xData = Res_TruthTops
    t.CompileHistogram()
    s.AddObject(t)

    tc = TH1F()
    tc.Title =  "The Predicted Resonance Mass Derived From 'truth_jets_*'\n (with Detector Leptons)"
    tc.xTitle = "Mass (GeV)"
    tc.yTitle = "Entries"
    tc.xBins = 200
    tc.xData = Res_TruthJet
    tc.CompileHistogram()
    s.AddObject(tc)   

    tc_init = TH1F()
    tc_init.Title = "The Predicted Resonance Mass Derived From 'truth_jets_*'\n (with Detector Leptons) (Good Matching)"
    tc_init.xTitle = "Mass (GeV)"
    tc_init.yTitle = "Entries"
    tc_init.xBins = 200
    tc_init.xData = Res_TruthJet_NoAnomaly
    tc_init.CompileHistogram()
    s.AddObject(tc_init)
    
    s.SaveFigure()


    # Comparison of Top mass from truthjets vs top_child information + No Anomalous Event matching 
    s = SubfigureCanvas()
    s.Filename = "ResonanceMassDetector"
 
    t = TH1F() 
    t.Title = "The Mass of Resonance Using 'truth_top_*'"
    t.xTitle = "Mass (GeV)"
    t.yTitle = "Entries"
    t.xBins = 200
    t.xData = Res_TruthTops
    t.CompileHistogram()
    s.AddObject(t)

    tc = TH1F()
    tc.Title =  "The Predicted Resonance Mass Derived From 'truth_jets_*'\n (with Detector Leptons)"
    tc.xTitle = "Mass (GeV)"
    tc.yTitle = "Entries"
    tc.xBins = 200
    tc.xData = Res_TruthJet
    tc.CompileHistogram()
    s.AddObject(tc)   

    tc_init = TH1F()
    tc_init.Title = "The Predicted Resonance Mass Derived From 'jets_*'\n (with Detector Leptons)"
    tc_init.xTitle = "Mass (GeV)"
    tc_init.yTitle = "Entries"
    tc_init.xBins = 200
    tc_init.xData = Res_Jet
    tc_init.CompileHistogram()
    s.AddObject(tc_init)
    
    s.SaveFigure()
    
    return True

def TestBackGroundProcesses():
    def CreateEvents(direc, event):
        ev = EventGenerator(direc, Stop = event)
        ev.SpawnEvents()
        ev.CompileEvent(SingleThread = True)
        return ev

    def GetNJets(ev, tree):
        Jet_Number = []
        for i in ev.Events:
            Event = ev.Events[i][tree]
            
            n = 0
            for k in Event.DetectorParticles:
                if k.Type == "jet":
                    n += 1
            Jet_Number.append(n)
        return Jet_Number
    
    dir_ttbar = "/CERN/Grid/Samples/NAF/2021-05-05-2cRC-all/mc16a/postProcessed_ttbar_PhPy8_Total.root"
    dir_4t = "/CERN/Grid/Samples/NAF/2021-05-05-2cRC-all/mc16a/postProcessed_4tops_aMCPy8_AFII.root"
    dir_SingleT = "/CERN/Grid/Samples/NAF/2021-05-05-2cRC-all/mc16a/postProcessed_SingleTop.root"
    dir_SingleT_Rare = "/CERN/Grid/Samples/NAF/2021-05-05-2cRC-all/mc16a/postProcessed_SingleTop_rare.root"
    
    dir_ttH = "/CERN/Grid/Samples/NAF/2021-05-05-2cRC-all/mc16a/postProcessed_ttH.root"
    dir_ttW = "/CERN/Grid/Samples/NAF/2021-05-05-2cRC-all/mc16a/postProcessed_ttW.root"

    dir_ttZ = "/CERN/Grid/Samples/NAF/2021-05-05-2cRC-all/mc16a/postProcessed_ttZ.root"
    dir_VH = "/CERN/Grid/Samples/NAF/2021-05-05-2cRC-all/mc16a/postProcessed_VH.root"

    dir_VV = "/CERN/Grid/Samples/NAF/2021-05-05-2cRC-all/mc16a/postProcessed_VV.root"
    dir_Wjets = "/CERN/Grid/Samples/NAF/2021-05-05-2cRC-all/mc16a/postProcessed_Wjets_Sherpa221.root"

    dir_Zjets_ee = "/CERN/Grid/Samples/NAF/2021-05-05-2cRC-all/mc16a/postProcessed_Zjets_ee_Sherpa221.root"
    dir_Zjets_mumu = "/CERN/Grid/Samples/NAF/2021-05-05-2cRC-all/mc16a/postProcessed_Zjets_mumu_Sherpa221.root"
    dir_Zjets_tautau = "/CERN/Grid/Samples/NAF/2021-05-05-2cRC-all/mc16a/postProcessed_Zjets_tautau_Sherpa221.root"

    
    Processes = [dir_ttbar, dir_4t, dir_SingleT, dir_SingleT_Rare, dir_ttH, dir_VH, dir_VV, dir_Wjets, dir_Zjets_ee, dir_Zjets_tautau, dir_Zjets_mumu]
    Map = {}
    for i in Processes:
        p = i.split("/")
        proc = p[len(p) - 1].strip(".root")
        name = "-".join(proc.split("_")[1:])
        Map[name] = i
        
        ev = CreateEvents(i, 5000)
        PickleObject(ev, proc)
   
    Jets = []
    Names = []
    for i in Map:
        ev = UnpickleObject("postProcessed_" + i.replace("-", "_"))
        Jets.append(GetNJets(ev, "tree"))
        Names.append(i)
    
    J = []
    for i in Jets:
        l = 0
        for k in i:
            l += k
        J.append(k)
    
    Njet_P = TH2F()
    Njet_P.Title = "N-Jets vs Process Considered"
    Njet_P.Filename = "n_jets_process"
    Njet_P.yData = Jets
    Njet_P.xData = Names
    Njet_P.yMin = 0
    Njet_P.xTitle = "Process"
    Njet_P.yTitle = "N-Jets"
    Njet_P.SaveFigure("Plots/Njets/")
    return True

def TestGNNMonitor():
    def Signal(a):
        return int(a.Signal)

    def Energy(a):
        return float(a.e)
    
    def Charge(a):
        return float(a.Signal)

    ev = UnpickleObject("SignalSample.pkl")
    Loader = GenerateDataLoader()
    Loader.AddNodeFeature("e", Energy)
    Loader.AddNodeFeature("C", Charge)
    Loader.AddNodeTruth("y", Signal)
    Loader.AddSample(ev, "nominal", "TruthTops")
    Loader.ToDataLoader()

    Sig = GenerateDataLoader()
    Sig.AddNodeFeature("e", Energy)
    Sig.AddNodeFeature("C", Charge)
    Sig.AddNodeTruth("y", Signal)
    Sig.AddSample(ev, "nominal", "TruthTops")

    op = Optimizer(Loader)
    op.DefaultBatchSize = 100
    op.Epochs = 200
    op.kFold = 10
    op.LearningRate = 1e-6
    op.WeightDecay = 1e-4
    op.DefineEdgeConv(2, 2)
    op.kFoldTraining()
    op.ApplyToDataSample(Sig, "Sig")    

    eva = EvaluationMetrics()
    eva.Sample = op
    eva.AddTruthAttribute("Signal")
    eva.AddPredictionAttribute("Sig")
    eva.ProcessSample()
    eva.LossTrainingPlot("Plots/GNN_Performance_Plots/")

    return True

def KinematicsPlotting():
    
    Events = UnpickleObject("SignalSample.pkl")

    d_ETA_Edge_SI = TH1F()
    d_ETA_Edge_DI = TH1F()
    d_ETA_Edge_SI.Title = "Same Index"
    d_ETA_Edge_DI.Title = "Different Index"
    d_ETA_Edge_SI.xTitle = "delta eta"
    d_ETA_Edge_DI.xTitle = "delta eta"
    d_ETA_Edge_SI.xBins = 250 
    d_ETA_Edge_DI.xBins = 250 
    d_ETA_Edge_SI.Filename = "Delta_ETA_Same_Index" 
    d_ETA_Edge_DI.Filename = "Delta_ETA_Different_Index" 
    d_ETA_Edge_SI.xMin = -5
    d_ETA_Edge_SI.xMax = 5
    d_ETA_Edge_DI.xMin = -5
    d_ETA_Edge_DI.xMax = 5

    d_Energy_Edge_SI = TH1F()
    d_Energy_Edge_DI = TH1F()
    d_Energy_Edge_SI.Title = "Same Index"
    d_Energy_Edge_DI.Title = "Different Index"
    d_Energy_Edge_SI.xTitle = "delta energy (GeV)"
    d_Energy_Edge_DI.xTitle = "delta energy (GeV)"
    d_Energy_Edge_SI.xBins = 250 
    d_Energy_Edge_DI.xBins = 250 
    d_Energy_Edge_SI.Filename = "Delta_Energy_Same_Index" 
    d_Energy_Edge_DI.Filename = "Delta_Energy_Different_Index" 
    d_Energy_Edge_SI.xMin = -1.25*1e3
    d_Energy_Edge_SI.xMax = 1.25*1e3
    d_Energy_Edge_DI.xMin = -1.25*1e3
    d_Energy_Edge_DI.xMax = 1.25*1e3


    d_PHI_Edge_SI = TH1F()
    d_PHI_Edge_DI = TH1F()
    d_PHI_Edge_SI.Title = "Same Index"
    d_PHI_Edge_DI.Title = "Different Index"
    d_PHI_Edge_SI.xTitle = "delta phi (rad)"
    d_PHI_Edge_DI.xTitle = "delta phi (rad)"
    d_PHI_Edge_SI.xBins = 250 
    d_PHI_Edge_DI.xBins = 250 
    d_PHI_Edge_SI.Filename = "Delta_PHI_Same_Index" 
    d_PHI_Edge_DI.Filename = "Delta_PHI_Different_Index" 
    d_PHI_Edge_SI.xMin = -6
    d_PHI_Edge_SI.xMax = 6
    d_PHI_Edge_DI.xMin = -6
    d_PHI_Edge_DI.xMax = 6

    d_PT_Edge_SI = TH1F()
    d_PT_Edge_DI = TH1F()
    d_PT_Edge_SI.Title = "Same Index"
    d_PT_Edge_DI.Title = "Different Index"
    d_PT_Edge_SI.xTitle = "pt (GeV)"
    d_PT_Edge_DI.xTitle = "pt (GeV)"
    d_PT_Edge_SI.xBins = 250 
    d_PT_Edge_DI.xBins = 250 
    d_PT_Edge_SI.Filename = "Delta_Pt_Same_Index" 
    d_PT_Edge_DI.Filename = "Delta_Pt_Different_Index" 
    d_PT_Edge_SI.xMin = -0.6*1e3
    d_PT_Edge_SI.xMax = 0.6*1e3
    d_PT_Edge_DI.xMin = -0.6*1e3
    d_PT_Edge_DI.xMax = 0.6*1e3

    Mass_Edge_SI = TH1F()
    Mass_Edge_DI = TH1F()
    Mass_Edge_SI.Title = "Same Index"
    Mass_Edge_DI.Title = "Different Index"
    Mass_Edge_SI.xTitle = "Mass (MeV)"
    Mass_Edge_DI.xTitle = "Mass (MeV)"
    Mass_Edge_SI.xBins = 250 
    Mass_Edge_DI.xBins = 250 
    Mass_Edge_SI.Filename = "Mass_Same_Index" 
    Mass_Edge_DI.Filename = "Mass_Different_Index" 
    Mass_Edge_SI.xMin = -1e3
    Mass_Edge_SI.xMax = 1e3
    Mass_Edge_DI.xMin = -1e3
    Mass_Edge_DI.xMax = 1e3

    Normalized_Mass_Edge_SI = TH1F()
    Normalized_Mass_Edge_DI = TH1F()
    Normalized_Mass_Edge_SI.Title = "Same Index"
    Normalized_Mass_Edge_DI.Title = "Different Index"
    Normalized_Mass_Edge_SI.xTitle = "Mass (MeV)"
    Normalized_Mass_Edge_DI.xTitle = "Mass (MeV)"
    Normalized_Mass_Edge_SI.xBins = 500
    Normalized_Mass_Edge_DI.xBins = 500
    Normalized_Mass_Edge_SI.Filename = "Normalized_Mass_Same_Index" 
    Normalized_Mass_Edge_DI.Filename = "Normalized_Mass_Different_Index" 
    Normalized_Mass_Edge_SI.xMin = 0
    Normalized_Mass_Edge_SI.xMax = 0.25
    Normalized_Mass_Edge_DI.xMin = 0
    Normalized_Mass_Edge_DI.xMax = 0.25

    Aggre_Kine_Edge_SI = TH1F()
    Aggre_Kine_Edge_DI = TH1F()
    Aggre_Kine_Edge_SI.Title = "Same Index"
    Aggre_Kine_Edge_DI.Title = "Different Index"
    Aggre_Kine_Edge_SI.xTitle = "Arb."
    Aggre_Kine_Edge_DI.xTitle = "Arb."
    Aggre_Kine_Edge_SI.xBins = 10000
    Aggre_Kine_Edge_DI.xBins = 10000
    Aggre_Kine_Edge_SI.Filename = "Aggre_Kin_Same_Index" 
    Aggre_Kine_Edge_DI.Filename = "Aggre_Kin_Different_Index" 
    Aggre_Kine_Edge_SI.xMin = 0
    Aggre_Kine_Edge_SI.xMax = 50
    Aggre_Kine_Edge_DI.xMin = 0
    Aggre_Kine_Edge_DI.xMax = 50

    Ratio_Kine_Edge_SI = TH1F()
    Ratio_Kine_Edge_DI = TH1F()
    Ratio_Kine_Edge_SI.Title = "Same Index"
    Ratio_Kine_Edge_DI.Title = "Different Index"
    Ratio_Kine_Edge_SI.xTitle = "Arb."
    Ratio_Kine_Edge_DI.xTitle = "Arb."
    Ratio_Kine_Edge_SI.xBins = 1000
    Ratio_Kine_Edge_DI.xBins = 1000
    Ratio_Kine_Edge_SI.Filename = "Ratio_Kin_Same_Index" 
    Ratio_Kine_Edge_DI.Filename = "Ratio_Kin_Different_Index" 
    Ratio_Kine_Edge_SI.xMin = -5
    Ratio_Kine_Edge_SI.xMax = 5
    Ratio_Kine_Edge_DI.xMin = -5
    Ratio_Kine_Edge_DI.xMax = 5

    dR_Edge_SI = TH1F()
    dR_Edge_DI = TH1F()
    dR_Edge_SI.Title = "Same Index"
    dR_Edge_DI.Title = "Different Index"
    dR_Edge_SI.xTitle = "dR"
    dR_Edge_DI.xTitle = "dR"
    dR_Edge_SI.xBins = 250 
    dR_Edge_DI.xBins = 250 
    dR_Edge_SI.Filename = "DeltaR_Same_Index" 
    dR_Edge_DI.Filename = "DeltaR_Different_Index" 
    dR_Edge_SI.xMin = -7
    dR_Edge_SI.xMax = 7
    dR_Edge_DI.xMin = -7
    dR_Edge_DI.xMax = 7

    SignalTops = TH1F()
    SignalTops.Title = "Signal"
    SignalTops.xTitle = "Mass (GeV)"
    SignalTops.xBins = 250 
    SignalTops.Filename = "Mass_Signal_Tops" 
    SignalTops.xMin = 0
    SignalTops.xMax = 180

    SpectatorTops = TH1F()
    SpectatorTops.Title = "Spectator"
    SpectatorTops.xTitle = "Mass (GeV)"
    SpectatorTops.xBins = 250 
    SpectatorTops.Filename = "Mass_Spectator_Top" 
    SpectatorTops.xMax = 180
    SpectatorTops.xMin = 0

    for i in Events.Events:
        pc = Events.Events[i]["nominal"].TruthChildren

        for e_i in pc:
            for e_j in pc: 
                if e_i == e_j:
                    continue
               
                P = Particle(True)
                P.Decay.append(e_i)
                P.Decay.append(e_j)
                P.CalculateMassFromChildren()

                e_i.CalculateMass()
                e_j.CalculateMass()

                agr = abs((e_i.eta - e_j.eta) / (e_i.eta + e_j.eta +1)) + abs((e_i.phi - e_j.phi) / (e_i.phi + e_j.phi +1)) + abs((e_i.e - e_j.e) / (e_i.e + e_j.e +1)) 

                if (e_i.pt > e_j.pt):
                    r = abs((e_j.eta) / (e_i.eta +1)) # + abs(e_i.phi / (e_j.phi +1))  + abs(e_i.e / (e_j.e +1))  + abs(e_i.pt / (e_j.pt +1)) 
                else:
                    r = abs((e_i.eta) / (e_j.eta +1)) # + abs(e_i.phi / (e_j.phi +1))  + abs(e_i.e / (e_j.e +1))  + abs(e_i.pt / (e_j.pt +1)) 

                if e_i.Index == e_j.Index:
                    Mass_Edge_SI.xData.append(P.Mass_GeV) 
                    d_ETA_Edge_SI.xData.append(e_i.eta - e_j.eta)
                    d_PHI_Edge_SI.xData.append(e_i.phi - e_j.phi)
                    d_Energy_Edge_SI.xData.append(float(e_i.e - e_j.e) / 1000)
                    d_PT_Edge_SI.xData.append(float(e_i.pt - e_j.pt)/ 1000)
                    dR_Edge_SI.xData.append(e_i.DeltaR(e_j))
                    Normalized_Mass_Edge_SI.xData.append( abs((e_i.Mass_GeV - e_j.Mass_GeV)) / P.Mass_GeV )
                    Aggre_Kine_Edge_SI.xData.append( agr + (1 / (P.Mass_GeV+1)) + (1 / (e_i.DeltaR(e_j) +1) ))
                    Ratio_Kine_Edge_SI.xData.append( r ); 

                elif e_i.Index != e_j.Index:
                    Mass_Edge_DI.xData.append(P.Mass_GeV) 
                    d_ETA_Edge_DI.xData.append(e_i.eta - e_j.eta)
                    d_PHI_Edge_DI.xData.append(e_i.phi - e_j.phi)
                    d_Energy_Edge_DI.xData.append(float(e_i.e - e_j.e) / 1000)
                    d_PT_Edge_DI.xData.append(float(e_i.pt - e_j.pt)/ 1000)
                    dR_Edge_DI.xData.append(e_i.DeltaR(e_j))
                    Normalized_Mass_Edge_DI.xData.append( abs((e_i.Mass_GeV - e_j.Mass_GeV)) / P.Mass_GeV )
                    Aggre_Kine_Edge_DI.xData.append( agr + (1 / (P.Mass_GeV+1)) + (1 / (e_i.DeltaR(e_j) +1) ))
                    Ratio_Kine_Edge_DI.xData.append( r ); 

        mass = [Particle(True), Particle(True), Particle(True), Particle(True)]
        for e_i in pc:
            mass[e_i.Index].Decay.append(e_i)
            mass[e_i.Index].Signal = e_i.Signal 
        
        for e_i in mass:
            e_i.CalculateMassFromChildren()
            if e_i.Signal == 1:
                SignalTops.xData.append(e_i.Mass_GeV)
            else:
                SpectatorTops.xData.append(e_i.Mass_GeV)

    Mass_Edge_SI.SaveFigure("Plots/Kinematics/")
    d_ETA_Edge_SI.SaveFigure("Plots/Kinematics/")
    d_PHI_Edge_SI.SaveFigure("Plots/Kinematics/")
    d_Energy_Edge_SI.SaveFigure("Plots/Kinematics/")
    d_PT_Edge_SI.SaveFigure("Plots/Kinematics/")
    dR_Edge_SI.SaveFigure("Plots/Kinematics/")
    Mass_Edge_DI.SaveFigure("Plots/Kinematics/")
    d_ETA_Edge_DI.SaveFigure("Plots/Kinematics/")
    d_PHI_Edge_DI.SaveFigure("Plots/Kinematics/")
    d_Energy_Edge_DI.SaveFigure("Plots/Kinematics/")
    d_PT_Edge_DI.SaveFigure("Plots/Kinematics/")
    dR_Edge_DI.SaveFigure("Plots/Kinematics/")
    Normalized_Mass_Edge_SI.SaveFigure("Plots/Kinematics/")
    Normalized_Mass_Edge_DI.SaveFigure("Plots/Kinematics/")
    SignalTops.SaveFigure("Plots/Kinematics/")
    SpectatorTops.SaveFigure("Plots/Kinematics/")
    Aggre_Kine_Edge_DI.SaveFigure("Plots/Kinematics/")
    Aggre_Kine_Edge_SI.SaveFigure("Plots/Kinematics/")

    # Combine the figures into a single one 
    Mass_Edge = CombineHistograms()
    Mass_Edge.Histograms = [Mass_Edge_SI, Mass_Edge_DI]
    Mass_Edge.Title = "Mass of Particle Edges from (un)common Parent Index"
    Mass_Edge.Filename = "Edge_Mass.png"
    Mass_Edge.Save("Plots/Kinematics/ComparativePlots/")

    dR_Edge = CombineHistograms()
    dR_Edge.Histograms = [dR_Edge_SI, dR_Edge_DI]
    dR_Edge.Title = "$\Delta$R of Particle Edges from (un)common Parent Index"
    dR_Edge.Filename = "Edge_dR.png"
    dR_Edge.Save("Plots/Kinematics/ComparativePlots/")

    d_phi_Edge = CombineHistograms()
    d_phi_Edge.Histograms = [d_PHI_Edge_SI, d_PHI_Edge_DI]
    d_phi_Edge.Title = "$\Delta \phi$ of Particle Edges from (un)common Parent Index"
    d_phi_Edge.Filename = "Edge_delta_phi.png"
    d_phi_Edge.Save("Plots/Kinematics/ComparativePlots/")

    d_eta_Edge = CombineHistograms()
    d_eta_Edge.Histograms = [d_ETA_Edge_SI, d_ETA_Edge_DI]
    d_eta_Edge.Title = "$\Delta \eta$ of Particle Edges from (un)common Parent Index"
    d_eta_Edge.Filename = "Edge_delta_eta.png"
    d_eta_Edge.Save("Plots/Kinematics/ComparativePlots/")

    d_Energy_Edge = CombineHistograms()
    d_Energy_Edge.Histograms = [d_Energy_Edge_SI, d_Energy_Edge_DI]
    d_Energy_Edge.Title = "$\Delta$ Energy of Particle Edges from (un)common Parent Index"
    d_Energy_Edge.Filename = "Edge_delta_Energy.png"
    d_Energy_Edge.Save("Plots/Kinematics/ComparativePlots/")

    d_PT_Edge = CombineHistograms()
    d_PT_Edge.Histograms = [d_ETA_Edge_SI, d_ETA_Edge_DI]
    d_PT_Edge.Title = "$\Delta P_T$ of Particle Edges from (un)common Parent Index"
    d_PT_Edge.Filename = "Edge_delta_PT.png"
    d_PT_Edge.Save("Plots/Kinematics/ComparativePlots/")

    Normalized_Mass = CombineHistograms()
    Normalized_Mass.Histograms = [Normalized_Mass_Edge_SI, Normalized_Mass_Edge_DI]
    Normalized_Mass.Title = "$\Delta$ Particle Mass / Edge Mass from (un)common Parent Index"
    Normalized_Mass.Filename = "Normalized_Mass.png"
    Normalized_Mass.Save("Plots/Kinematics/ComparativePlots/")

    Aggr_Kine = CombineHistograms()
    Aggr_Kine.Histograms = [Aggre_Kine_Edge_SI, Aggre_Kine_Edge_DI]
    Aggr_Kine.Title = "Edge Kinematic Aggregation from (un)common Parent Index"
    Aggr_Kine.Filename = "Aggr_Kine.png"
    Aggr_Kine.Save("Plots/Kinematics/ComparativePlots/")

    R_Kine = CombineHistograms()
    R_Kine.Histograms = [Ratio_Kine_Edge_SI, Ratio_Kine_Edge_DI]
    R_Kine.Title = "Edge Kinematic Ratio from (un)common Parent Index"
    R_Kine.Filename = "Ratio_Kine.png"
    R_Kine.Save("Plots/Kinematics/ComparativePlots/")

    return True    
