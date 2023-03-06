from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Events import Event
from TruthTops import *
from TopChildren import *
from TruthJetMatching import * 
import os
import shutil

massPoints = ["1000"] # ["400", "500", "600", "700", "800", "900", "1000"]
Modes = ["Dilepton"]#, "SingleLepton"]

for Mode in Modes:
    for massPoint in massPoints:
        #direc = "/CERN/Samples/" + Mode + "/Collections/ttH_tttt_m" + massPoint + "/DAOD_TOPQ1.21955717._000001.root"
        direc = "/eos/home-t/tnommens/Processed/" + Mode + "/ttH_tttt_m" + massPoint
        Ana = Analysis()
        Ana.InputSample("tttt", direc)
        Ana.Event = Event
        #Ana.EventStop = 100
        Ana.Threads = 12
        Ana.chnk = 1000
        Ana.EventCache = True
        Ana.DumpPickle = True
        Ana.Launch()
        
        # ------ Top Centric Plots ----- # 
        # Figures 1.1: "a" and "b"
        ResonanceDecayModes(Ana)
        
        # Figures 1.1: "c"
        ResonanceMassFromTops(Ana)
        
        # Figures 1.1: "d"
        DeltaRTops(Ana)
        
        # Figures 1.1: "e" - "f"
        TopKinematics(Ana)
        
        # ------ Top Child Centric Plots ----- # 
        # Figures 2.1:  "a"
        TopChildrenPDGID(Ana)
        
        # Figures 2.1: "b" - "d"
        ReconstructedMassFromChildren(Ana)
        ReconstructedMassFromChildrenWithoutNeutrinos(Ana)
        
        # Figures 2.1: "e" - "g" 
        DeltaRChildren(Ana)
        
        # Figures 2.1: "h"
        FractionPTChildren(Ana)

        # Figures 2.1: "i"
        DeltaRLepB(Ana)
        
        # Figures 2.1: "j":
        MassDiff(Ana)

        # Figures 2.1: "k" - "p"
        TopChildrenKinematics(Ana)

        # ------ Truth Jet Centric Plots ----- # 
        # Figures 3.1: "a" - "d"
        TruthJetPartons(Ana)
        
        # Figures 3.1: "e"
        PartonToChildTruthJet(Ana)
        
        # Figures 3.1: "f" and "g"
        eff = ReconstructedTopMassTruthJet(Ana)
        f = open(Mode + "_" + massPoint + ".txt", "w")
        f.write("\n".join([i + "-" + str(eff[i]) for i in eff]))
        f.close()
   
        # Figures 3.1: 
        DeltaRTruthJets(Ana) 

        os.makedirs("./" + Mode + "/" + massPoint, exist_ok = True)
        shutil.move("./Figures", "./" + Mode + "/" + massPoint)
        exit()
