from AnalysisTopGNN import Analysis 
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.Events import EventGraphChildren
from AnalysisTopGNN.Features import ApplyFeatures
#from BasicBaseLineModel.V3.BasicBaseLine import BasicBaseLineRecursion
from RecursiveNeutrino.V1.Recursion import Recursion

Ana = Analysis()
Ana.ProjectName = "PROJECT"
Ana.InputSample("bsm-1000", "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root")
#Ana.InputSample("ttbar", "/home/tnom6927/Downloads/samples/ttbar/DAOD_TOPQ1.27296255._000017.root")
Ana.Event = Event 
Ana.EventCache = False 

Ana.EventGraph = EventGraphChildren
Ana.DataCache = True
Ana.EventStop = 100

Ana.DumpPickle = False
Ana.DumpHDF5 = True
ApplyFeatures(Ana, "TruthChildren")
Ana.TrainingSampleName = "Children"
Ana.Device = "cuda"
Ana.Tree = "nominal"
Ana.kFolds = 10
Ana.Epochs = 10
Ana.BatchSize = 1
Ana.ContinueTraining = False
Ana.Optimizer = {"ADAM" : {"lr" : 1e-3, "weight_decay" : 1e-3}}
Ana.Model = Recursion()
Ana.DebugMode = "loss"
Ana.Launch()
