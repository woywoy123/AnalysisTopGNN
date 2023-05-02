from AnalysisTopGNN import Analysis
from AnalysisTopGNN.Events import Event
from Strategy import Common
from AnalysisTopGNN.Submission import Condor
from AnalysisTopGNN.IO import UnpickleObject
from plotting import PlotEfficiency

direc = "/atlasgpfs01/usatlas/data/eleboulicaut/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root"
#direc = "/nfs/dust/atlas/user/sitnikov/ntuples_for_classifier/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root"
Ana = Analysis()
Ana.ProjectName = "Analysis_50events"
Ana.Event = Event
Ana.EventCache = True
Ana.DumpPickle = True
Ana.InputSample("bsm-1000", direc)
Ana.AddSelection("bsm", Common)
Ana.MergeSelection("bsm")
Ana.chnk = 1
Ana.EventStop = 50
Ana.Threads = 1
Ana.Launch()

x = UnpickleObject("Analysis_50events/Selections/Merged/bsm")

# print(x._CutFlow)
# print(x._Residual)
# print(x._TimeStats)
# import json
# print(json.dumps(x.masses, indent=1))
# print(Ana[x._hash[0]]) #< returns the event of this given hash.

PlotEfficiency(x, "case")
PlotEfficiency(x, "object")
out_string = ""
for object_type in x.efficiency_avg.keys():
    for case_num in x.efficiency_avg[object_type].keys():
        for method in x.efficiency_avg[object_type][case_num].keys():
            out_string += f"Average event efficiency for object type {object_type}, case {case_num}, method {method} is {sum(x.efficiency_avg[object_type][case_num][method]) / len(x.efficiency_avg[object_type][case_num][method])}\n"

print(out_string)
f = open("avg_efficiencies.txt", "w")
f.write(out_string)
f.close()
                


# Here is an example Condor Submission scripter. Basically remove Ana.Launch() to compile this.
# T = Condor()
# T.ProjectName = "Analysis"
# T.CondaEnv = "GNN"
# T.AddJob("bsm-1000", Ana, memory = None, time = None)
# T.DumpCondorJobs()
# T.LocalDryRun()
