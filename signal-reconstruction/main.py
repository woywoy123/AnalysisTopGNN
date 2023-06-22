from AnalysisG import Analysis
from AnalysisG.Events.Events.CommonSM4topEvent import Event
from Strategy import Common
from AnalysisG.Submission import Condor
from AnalysisG.IO import UnpickleObject
from plotting import PlotEfficiency
import copy
from mtt_reconstruction import MttReconstructor
from Strategy import Common
import uproot
import numpy as np
import os


def submit_jobs():
    # direc = "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000"#"/atlasgpfs01/usatlas/data/eleboulicaut/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root"
    root_dir = "/nfs/dust/atlas/user/sitnikov/signal-comparison/common-fw_tag212120/final"
    mc_cpgn = {
                "mc16a" : root_dir + "/mc16a/2lss3lge1DL1r",
                "mc16d" : root_dir + "/mc16d/2lss3lge1DL1r",
                "mc16e" : root_dir + "/mc16e/2lss3lge1DL1r",
    }
    Quant = 1

    def CreateEvents(mc_cg):
        Ana = Analysis()
        this_pth = mc_cpgn[mc_cg]
        smpls = Ana.ListFilesInDir(this_pth, ".root")
        Ana = Ana.Quantize(smpls[this_pth], Quant)
        out = []
        for i in Ana:
            ana = Analysis()
            ana.Event = Event
            ana.EventCache = True
            ana.chnk = 10
            ana.Threads = 12
            ana.InputSample(mc_cg, {this_pth : i})
            ana.AddSelection("bsm", Common)
            # ana.EventStop = int(ana.chnk * ana.Threads)
            out.append(ana)
        return out

    T = Condor()
    T.ProjectName = "Analysis"
    T.PythonVenv = "/nfs/dust/atlas/user/sitnikov/analysistopgnn/setup-scripts/source_this.sh"

    # Create the event cache.
    waitforme = []
    for mc in mc_cpgn:
        jbs = CreateEvents(mc)
        base = "event_" + mc + "_ev"
        for j, its in zip(jbs, range(len(jbs))):
            j_name = base + str(its)
            T.AddJob(j_name, j, "2GB", "4h")
            waitforme.append(j_name)

    # Create Final merge
    mrg = Analysis()
    mrg.MergeSelection("bsm")
    T.AddJob("mrg", mrg, memory = "8GB", time = "8h", waitfor = waitforme)
    T.DumpCondorJobs
    # T.TestCondorShell
    T.SubmitToCondor

def process_result():
    # mrg = Analysis()
    # mrg.MergeSelection("bsm")
    # mrg.ProjectName = "Analysis"
    # mrg.Launch
    x = UnpickleObject("Analysis/Selections/Merged/bsm")
    print(x.CutFlow)
    # if not os.path.exists('mtt_ntuples'):
    #     os.makedirs('mtt_ntuples')
    # for ROOTName in x.masses:
    #     filename = ROOTName.split('/')[-1]
    #     if 'mc16a' in ROOTName:
    #         dir = 'mc16a'
    #     elif 'mc16e' in ROOTName:
    #         dir = 'mc16e'
    #     elif 'mc16d' in ROOTName:
    #         dir = 'mc16d'
    #     elif 'data' in ROOTName:
    #         dir = 'data'
    #     else:
    #         dir = ''
    #     if not os.path.exists('mtt_ntuples/' + dir):
    #         os.makedirs('mtt_ntuples/' + dir)
    #     print(filename)
    #     with uproot.recreate(f'mtt_ntuples/{dir}/{filename}') as file:
    #         file['tree'] = {'mtt' : x.masses[ROOTName], 'eventNumber' : x.eventNumbers[ROOTName], 'runNumber' : x.runNumbers[ROOTName], 'mcChannelNumber' : x.mcChannelNumbers[ROOTName]}


from AnalysisG.Plotting import TH1F, TH2F, CombineTH1F

def TemplatePlotsTH1F():
    Plots = {
                # "NEvents" : x.NEvents, 
                "ATLASLumi" : 1, 
                "Style" : "ATLAS", 
                "LaTeX": False,
                "OutputDirectory" : "./Figures/", 
                "yTitle" : "Entries (a.u.)", 
                "yMin" : 0, "xMin" : 0
            }
    return Plots

def make_plots():
    import random
    x = UnpickleObject("Analysis/Selections/bsm/0x1c250c1370644262.pkl")
    print(x.CutFlow)
    print(x.masses.keys())
    return
    dummy_data = [random.random() for i in range(1000)]
    other_dummy_data = [1 for i in range(10)]
    Plots_ = TemplatePlotsTH1F()
    Plots_["Title"] = f"Dummy plot"
    Plots_["xTitle"] = "Dummy data"
    Plots_["Histograms"] = []
    for data in [dummy_data, other_dummy_data]:
        Plots = {}
        Plots["Title"] = f"Some dummy data {data[0]}" 
        Plots["xData"] = data
        thc = TH1F(**Plots)
        Plots_["Histograms"].append(thc)
    Plots_["xMin"] = 0
    Plots_["xMax"] = 1
    Plots_["xStep"] = 0.1
    Plots_["Filename"] = f"Testing"
    tc = CombineTH1F(**Plots_)
    tc.SaveFigure()

# make_plots()
submit_jobs()
# process_result()





# for y in x.masses['Jet'][9]:
#     print(y)

# print(x._CutFlow)
# print(x._Residual)
# print(x._TimeStats)
# import json
# print(json.dumps(x.masses, indent=1))
# print(Ana[x._hash[0]]) #< returns the event of this given hash.

# PlotEfficiency(x, "case")
# PlotEfficiency(x, "object")
# out_string = ""
# for object_type in x.efficiency_avg.keys():
#     for case_num in x.efficiency_avg[object_type].keys():
#         for method in x.efficiency_avg[object_type][case_num].keys():
#             out_string += f"Average event efficiency for object type {object_type}, case {case_num}, method {method} is {sum(x.efficiency_avg[object_type][case_num][method]) / len(x.efficiency_avg[object_type][case_num][method])}\n"

# print(out_string)
# f = open("avg_efficiencies.txt", "w")
# f.write(out_string)
# f.close()
                


# Here is an example Condor Submission scripter. Basically remove Ana.Launch() to compile this.
#T = Condor()
#T.ProjectName = "Analysis"
#T.CondaEnv = None 
#T.PythonVenv = "/nfs/dust/atlas/user/sitnikov/analysistopgnn/setup-scripts/source_this.sh"
#T.AddJob("bsm-1000", Ana, memory = None, time = None)
#T.DumpCondorJobs
# T.TestCondorShell
#T.SubmitToCondor
# T.LocalDryRun()
