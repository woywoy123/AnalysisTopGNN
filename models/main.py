from AnalysisTopGNN import Analysis 
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.Events import EventGraphChildren
from AnalysisTopGNN.Features import ApplyFeatures
#from BasicBaseLineModel.V3.BasicBaseLine import BasicBaseLineRecursion
#from PassNet.V1.PassNet import *
from PathNet.V1.PathNet import *

Ana = Analysis()
Ana.ProjectName = "PROJECT-small"
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
Ana.Epochs = 100
Ana.BatchSize = 10
Ana.ContinueTraining = False
Ana.Optimizer = {"ADAM" : {"lr" : 1e-3, "weight_decay" : 1e-3}}
Ana.Model = PathNet()
Ana.DebugMode = "loss"
Ana.Launch()

