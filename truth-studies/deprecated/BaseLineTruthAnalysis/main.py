from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.IO import PickleObject, UnpickleObject
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F
from SelectionTests import *
from Dilepton import *
from TestFromRes import *
from Dilepton_withNeutrinoReco import *

massPoints = ["1000"] # ["400", "500", "600", "700", "800", "900", "1000"]
Modes = ["Dilepton"]#, "SingleLepton"]

for Mode in Modes:
    for massPoint in massPoints:
        direc = "/eos/home-t/tnommens/Processed/" + Mode + "/ttH_tttt_m" + massPoint
        Ana = Analysis()
        Ana.InputSample("tttt", direc)
        Ana.Event = Event
        Ana.EventStop = 100
        Ana.ProjectName = Mode + (f"_EventStop{Ana.EventStop}" if Ana.EventStop else "")
        Ana.Threads = 12
        Ana.chnk = 1000
        Ana.EventCache = True
        Ana.DumpPickle = True
        Ana.Launch()

    # Selection(Ana)
    #DileptonAnalysis(Ana)
    DileptonAnalysis_withNeutrinoReco(Ana)
    #TestFromRes(Ana)



    



 

