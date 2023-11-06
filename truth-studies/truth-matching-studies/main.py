from AnalysisG import Analysis
from AnalysisG.Events import Event
from AnalysisG.IO import UnpickleObject, PickleObject, nTupler

from Studies.Resonance.ZPrimePtMass import ZPrimeMatrix
import PlottingCode.Resonance_ZPrimePtMass as ZPrime

import Studies.Resonance.ResonanceTruthTops as RTT_Sel
import PlottingCode.ResonanceTruthTops as RTT_Plot

#import Studies.Resonance.ResonanceTruthChildren as RTC_Sel
#import PlottingCode.ResonanceTruthChildren as RTC_Plot
#
#import Studies.Resonance.ResonanceFromTruthJets as RTJ_Sel
#import PlottingCode.ResonanceFromTruthJets as RTJ_Plot
#
#import Studies.Resonance.ResonanceFromJets as RJJ_Sel
#import PlottingCode.ResonanceFromJets as RJJ_Plot

import Studies.TruthTops.TopDecay as TTT_Sel
import PlottingCode.TopDecay as TTT_Plot

#import Studies.TruthTops.TopsFromTruthJets as TTJ_Sel
#import PlottingCode.TopsFromTruthJets as TTJ_Plot
#
#import Studies.TruthTops.TopsFromJets as TJ_Sel
#import PlottingCode.TopsFromJets as TJ_Plot
#
#import Studies.TruthChildren.TruthChildrenKinematics as TCK_Sel
#import PlottingCode.TruthChildrenKinematics as TCK_Plot
#
import Studies.Event.TruthEvent as ETE_Sel
import PlottingCode.TruthEvent as ETE_Plot

#import Studies.Event.EventNeutrino as EN_Sel
#import PlottingCode.EventNeutrino as EN_Plot
import os
import shutil

toRun = [
        #"ZPrimeMatrix", 
        #"ResonanceDecayModes",
        #"ResonanceMassFromTops", 
        #"ResonanceDeltaRTops",
        #"ResonanceTopKinematics",
        #"EventNTruthJetAndJets",
        #"EventMETImbalance",
        "TopDecayModes",
        #"ResonanceMassFromChildren", 
        #"DeltaRChildren", 
        #"TruthChildrenKinematics", 
        #"EventNuNuSolutions", 
        #"ResonanceMassTruthJets", 
        #"ResonanceMassTruthJetsNoSelection", 
        #"TopMassTruthJets", 
        #"TopTruthJetsKinematics", 
        #"ResonanceMassJets", 
        #"TopMassJets", 
        #"MergedTopsTruthJets", 
        #"MergedTopsJets"
]

studies = {
            "ZPrimeMatrix" : ZPrimeMatrix,
            "ResonanceDecayModes" : RTT_Sel.ResonanceDecayModes,
            "ResonanceMassFromTops" : RTT_Sel.ResonanceMassFromTops,
            "ResonanceDeltaRTops" : RTT_Sel.ResonanceDeltaRTops,
            "ResonanceTopKinematics" : RTT_Sel.ResonanceTopKinematics,
            "EventNTruthJetAndJets" : ETE_Sel.EventNTruthJetAndJets,
            "EventMETImbalance" : ETE_Sel.EventMETImbalance,
            "TopDecayModes" : TTT_Sel.TopDecayModes,
            #"ResonanceMassFromChildren" : RTC_Sel.ResonanceMassFromChildren,
            #"DeltaRChildren" : TCK_Sel.DeltaRChildren,
            #"TruthChildrenKinematics" : TCK_Sel.TruthChildrenKinematics, 
            #"EventNuNuSolutions" : EN_Sel.EventNuNuSolutions, 
            #"ResonanceMassTruthJets" : RTJ_Sel.ResonanceMassTruthJets, 
            #"ResonanceMassTruthJetsNoSelection" : RTJ_Sel.ResonanceMassTruthJetsNoSelection, 
            #"TopMassTruthJets" : TTJ_Sel.TopMassTruthJets, 
            #"TopTruthJetsKinematics" : TTJ_Sel.TopTruthJetsKinematics, 
            #"MergedTopsTruthJets" : TTJ_Sel.MergedTopsTruthJets, 
            #"ResonanceMassJets" : RJJ_Sel.ResonanceMassJets, 
            #"TopMassJets" : TJ_Sel.TopMassJets, 
            #"MergedTopsJets" : TJ_Sel.MergedTopsJets, 
}

studiesPlots = {
            "ZPrimeMatrix" : ZPrime.Plotting,
            "ResonanceDecayModes" : RTT_Plot.ResonanceDecayModes,
            "ResonanceMassFromTops" : RTT_Plot.ResonanceMassFromTops,
            "ResonanceDeltaRTops" : RTT_Plot.ResonanceDeltaRTops,
            "ResonanceTopKinematics" : RTT_Plot.ResonanceTopKinematics,
            "EventNTruthJetAndJets" : ETE_Plot.EventNTruthJetAndJets,
            "EventMETImbalance" : ETE_Plot.EventMETImbalance,
            "TopDecayModes" : TTT_Plot.TopDecayModes,
            #"ResonanceMassFromChildren" : RTC_Plot.ResonanceMassFromChildren, 
            #"DeltaRChildren" : TCK_Plot.DeltaRChildren,
            #"TruthChildrenKinematics" : TCK_Plot.TruthChildrenKinematics, 
            #"EventNuNuSolutions" : EN_Plot.EventNuNuSolutions, 
            #"ResonanceMassTruthJets" : RTJ_Plot.ResonanceMassTruthJets,
            #"ResonanceMassTruthJetsNoSelection" : RTJ_Plot.ResonanceMassTruthJetsNoSelection, 
            #"TopMassTruthJets" : TTJ_Plot.TopMassTruthJets, 
            #"TopTruthJetsKinematics" : TTJ_Plot.TopTruthJetsKinematics, 
            #"MergedTopsTruthJets" : TTJ_Plot.MergedTopsTruthJets,
            #"ResonanceMassJets" : RJJ_Plot.ResonanceMassJets, 
            #"TopMassJets" : TJ_Plot.TopMassJets, 
            #"MergedTopsJets" : TJ_Plot.MergedTopsJets, 
}


run_ana = False
run_tup = False
run_plt = True

if run_ana:
    smpl = os.environ["Samples"]
    Ana = Analysis()
    Ana.ProjectName = "analysis_truth"
    Ana.InputSample("BSM-4t-DL-1000", smpl + "ttZ-1000/")
    #Ana.InputSample("BSM-4t-DL-900", smpl + "ttZ-900/")
    #Ana.InputSample("BSM-4t-DL-800", smpl + "ttZ-800/")
    #Ana.InputSample("BSM-4t-DL-700", smpl + "ttZ-700/")
    #Ana.InputSample("BSM-4t-DL-600", smpl + "ttZ-600/")
    #Ana.InputSample("BSM-4t-DL-500", smpl + "ttZ-500/")
    #Ana.InputSample("BSM-4t-DL-400", smpl + "ttZ-400/")
    Ana.Event = Event
    Ana.EventStop = 2000
    Ana.Threads = 1
    Ana.Chunks = 1000
    Ana.EventCache = True
    Ana.GetSelection = False
    Ana.PurgeCache = False
    for i in toRun: Ana.AddSelection(studies[i])
    Ana.Launch()

# Debugging space
#    x = studies["ZPrimeMatrix"]()
#    for i in Ana: x.__processing__(i)
#    print(x)
#    exit()

if run_tup:
    nt = nTupler()
    nt.Chunks = 1000
    nt.ProjectName = "analysis_truth"
    for i in toRun: nt.This(i, "nominal")
    for i, j in nt.merged().items(): PickleObject(j.__getstate__(), "output/" + i)

if run_plt:
    fin = {}
    Ana = Analysis()
    for i in Ana.ls("output/"):
        name = i.split(".")[1]
        if name not in toRun: continue
        fin[name] = studies[name]()
        fin[name].__setstate__(UnpickleObject("output/" + i))

    for i in fin:
        print("Making Plots for: " + i)
        studiesPlots[i](fin[i])

