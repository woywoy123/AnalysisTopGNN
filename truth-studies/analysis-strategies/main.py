from plotting.double_leptonic.truthchildren import doubleleptonic_Plotting
from double_leptonic import DiLeptonic
from AnalysisG.Events import Event
from AnalysisG.IO import nTupler
from AnalysisG import Analysis
import os

smpls = os.environ["Samples"]

which_analysis = "double-leptonic:DiLeptonic"
run = True

_ana = which_analysis.split(":")
if _ana[0] == "double-leptonic": ana = DiLeptonic()

ana.__params__ = { "btagger" : "is_b" , "truth" : "children"}

samples = {
        "ttZ"   : smpls + "ttZ-1000",
        "other" : smpls + "other",
        "t"     : smpls + "t"    ,
        "tt"    : smpls + "tt"   ,
        "ttbar" : smpls + "ttbar",
        "ttH"   : smpls + "ttH"  ,
        "tttt"  : smpls + "tttt" ,
        "ttX"   : smpls + "ttX"  ,
        "ttXll" : smpls + "ttXll",
        "ttXqq" : smpls + "ttXqq",
        "V"     : smpls + "V"    ,
        "Vll"   : smpls + "Vll"  ,
        "Vqq"   : smpls + "Vqq"
}

if run:
    Ana = Analysis()
    Ana.ProjectName = _ana[1]
    for key in samples: Ana.InputSample(key, samples[key])
    Ana.Event = Event
    #Ana.EventStop = 1000
    Ana.EventCache = True
    Ana.Threads = 8
    Ana.chnk = 1000
    Ana.AddSelection(ana.__class__.__name__, ana)
    Ana.Launch()

tupler = nTupler(_ana[1] + "/Selections/" + _ana[1])
tupler.This(_ana[1] + " -> ", "nominal")
tupler.Threads = 6
x = tupler.merged()
doubleleptonic_Plotting(x[_ana[1]], "truthchildren")

