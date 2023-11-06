from plotting.double_leptonic.truthchildren import doubleleptonic_Plotting
from AnalysisG.IO import nTupler, PickleObject, UnpickleObject
from double_leptonic import DiLeptonic
from AnalysisG.Events import Event
from AnalysisG.Tools import Tools
from AnalysisG import Analysis
import os


smpls = os.environ["Samples"]
which_analysis = "double-leptonic:DiLeptonic"
_ana = which_analysis.split(":")
if _ana[0] == "double-leptonic": ana = DiLeptonic()

combinations = [
        ("is_b"        , "children"),
        ("btag_DL1r_60", "jets+truthleptons"),
        ("btag_DL1r_77", "jets+truthleptons"),
        ("btag_DL1r_85", "jets+truthleptons"),

        ("btag_DL1_60", "jets+truthleptons"),
        ("btag_DL1_77", "jets+truthleptons"),
        ("btag_DL1_85", "jets+truthleptons"),

        ("btag_DL1r_60", "detector"),
        ("btag_DL1r_77", "detector"),
        ("btag_DL1r_85", "detector"),

        ("btag_DL1_60",  "detector"),
        ("btag_DL1_77",  "detector"),
        ("btag_DL1_85",  "detector")
]

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


t = Tools()
all_smpls = []
for key in samples: all_smpls += t.lsFiles(samples[key])
quant = list(t.Quantize(all_smpls, 10))
run_cache = False
run_selection = False
run_ntpl = False

x = 0
for smpl in quant:
    if run_cache: pass
    else: break
    Ana = Analysis()
    Ana.ProjectName = _ana[1]
    Ana.InputSample("smpl-" + str(x), smpl)
    Ana.EventCache = True
    Ana.Event = Event
    Ana.Threads = 12
    Ana.Chunks = 1000
    Ana.Launch()
    x+=1



for pairs in combinations:
    tagger, truth = pairs
    ana.__params__ = { "btagger" : tagger , "truth" : truth}
    name = _ana[1] + "_" + tagger + "_" + truth.replace("+","-")
    x = 0
    for smpl in quant:
        if run_selection: pass
        else: break
        Ana = Analysis()
        Ana.ProjectName = _ana[1]
        Ana.InputSample("smpl-" + str(x), smpl)
        Ana.EventCache = True
        Ana.AddSelection(ana)
        Ana.Threads = 2
        Ana.Chunks = 1000
        Ana.Launch()
        x += 1

    if run_ntpl:
        tupler = nTupler()
        tupler.Threads = 12
        tupler.Chunks = 1000
        tupler.ProjectName = _ana[1]
        tupler.This("DiLeptonic -> ", "nominal")

        x = tupler.merged()
        tupler.rm(tupler.WorkingPath + "/SelectionCache")
        PickleObject(x["nominal.DiLeptonic"].__getstate__(), name)

    pkl = UnpickleObject(name)
    if pkl is None: continue
    ana.__setstate__(pkl)
    print("Building Plots: " + name)
    doubleleptonic_Plotting(ana, name)

