from AnalysisTopGNN import Analysis 
from AnalysisTopGNN.Events import Event 
from Strategy import Common 
from AnalysisTopGNN.Submission import Condor
from AnalysisTopGNN.IO import UnpickleObject

direc = "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root"
Ana = Analysis()
Ana.ProjectName = "Analysis"
Ana.Event = Event 
Ana.EventCache = True 
Ana.DumpPickle = True
Ana.InputSample("bsm-1000", direc)
Ana.AddSelection("bsm", Common)
Ana.MergeSelection("bsm")
Ana.chnk = 10
Ana.EventStop = 100
Ana.Launch()

x = UnpickleObject("Analysis/Selections/Merged/bsm")
print(x._CutFlow) 
print(x._Residual)
print(x._TimeStats)
print(Ana[x._hash[0]]) #< returns the event of this given hash.


# Here is an example Condor Submission scripter. Basically remove Ana.Launch() to compile this.
T = Condor()
T.ProjectName = "Analysis"
T.CondaEnv = "GNN"
T.AddJob("bsm-1000", Ana, memory = None, time = None)
#T.DumpCondorJobs()
#T.LocalDryRun()
