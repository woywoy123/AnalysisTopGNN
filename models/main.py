from AnalysisTopGNN import Analysis 
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.Events import EventGraphChildrenNoNu
from AnalysisTopGNN.Features import ApplyFeatures
#from BasicBaseLineModel.V3.BasicBaseLine import BasicBaseLineRecursion
from RecursiveNeutrino.V1.Recursion import Recursion

Ana = Analysis()
Ana.ProjectName = "PROJECT"
Ana.InputSample("bsm-1000", "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root")
Ana.Event = Event 
Ana.EventCache = True 

Ana.EventGraph = EventGraphChildrenNoNu
Ana.DataCache = True 
#Ana.EventStop = 100

Ana.DumpPickle = True 
ApplyFeatures(Ana, "TruthChildren")
Ana.TrainingSampleName = "Children"
Ana.Device = "cuda"
Ana.kFolds = 10
Ana.Epochs = 10
Ana.BatchSize = 10
Ana.Optimizer = {"ADAM" : {"lr" : 0.001, "weight_decay" : 0.001}}
Ana.Model = Recursion()
#Ana.DebugMode = "loss"
Ana.Launch()
