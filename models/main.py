from AnalysisG import Analysis
from AnalysisG.Events import Event
from AnalysisG.Events import GraphChildren, GraphChildrenNoNu


from AnalysisG.Events import GraphTruthJet, GraphDetector
from AnalysisG.Templates import ApplyFeatures
from BasicGraphNeuralNetwork.model import BasicGraphNeuralNetwork
from RecursiveGraphNeuralNetwork.model import RecursiveGraphNeuralNetwork


mode = "TruthChildrenNoNu"
modes = {"TruthJets": GraphTruthJet, "Jets": GraphDetector}
modes |= {"TruthChildren": GraphChildren, "TruthChildrenNoNu": GraphChildrenNoNu}


ttbar = [
    "DAOD_TOPQ1.25521412._000370.root",
    "DAOD_TOPQ1.25522886._000078.root",
    #"DAOD_TOPQ1.25522886._000246.root  DAOD_TOPQ1.25526070._000099.root",
    #"DAOD_TOPQ1.25521412._000806.root",
    #"DAOD_TOPQ1.25522886._000119.root",
    #"DAOD_TOPQ1.25522886._000247.root  DAOD_TOPQ1.25526070._000100.root",
    #"DAOD_TOPQ1.25521412._002194.root",
    #"DAOD_TOPQ1.25522886._000120.root",
    #"DAOD_TOPQ1.25522886._000248.root  DAOD_TOPQ1.25526070._000101.root",
    #"DAOD_TOPQ1.25521437._002568.root",
    #"DAOD_TOPQ1.25522886._000123.root",
    #"DAOD_TOPQ1.25522886._000251.root  DAOD_TOPQ1.25526070._000104.root",
    #"DAOD_TOPQ1.25521437._003198.root",
    #"DAOD_TOPQ1.25522886._000124.root",
    #"DAOD_TOPQ1.25522886._000252.root  DAOD_TOPQ1.25526070._000106.root",
    #"DAOD_TOPQ1.25521486._000037.root",
    #"DAOD_TOPQ1.25522886._000136.root",
    #"DAOD_TOPQ1.25522886._000265.root  DAOD_TOPQ1.25526070._000118.root",
    #"DAOD_TOPQ1.25521486._000090.root",
    #"DAOD_TOPQ1.25522886._000137.root",
    #"DAOD_TOPQ1.25522886._000266.root  DAOD_TOPQ1.25526070._000119.root",
    #"DAOD_TOPQ1.25521486._000091.root",
    #"DAOD_TOPQ1.25522886._000138.root",
    #"DAOD_TOPQ1.25522886._000267.root  DAOD_TOPQ1.25526070._000120.root",
]

bsm4t = [
    "DAOD_TOPQ1.21955717._000007.root",
    "DAOD_TOPQ1.21955743._000006.root",
    "DAOD_TOPQ1.21955743._000021.root",
    #"DAOD_TOPQ1.21955751._000014.root",
    #"DAOD_TOPQ1.21955717._000009.root",
    #"DAOD_TOPQ1.21955743._000008.root",
    #"DAOD_TOPQ1.21955751._000001.root",
    #"DAOD_TOPQ1.21955751._000016.root",
    #"DAOD_TOPQ1.21955717._000011.root",
    #"DAOD_TOPQ1.21955743._000010.root",
    #"DAOD_TOPQ1.21955751._000003.root",
    #"DAOD_TOPQ1.21955751._000018.root",
    #"DAOD_TOPQ1.21955717._000012.root",
    #"DAOD_TOPQ1.21955743._000014.root",
    #"DAOD_TOPQ1.21955751._000004.root",
    #"DAOD_TOPQ1.21955751._000019.root",
]


pth = "/home/tnom6927/Downloads/samples"

#Ana = Analysis()
#Ana.ProjectName = "Project"
#Ana.InputSample("bsm-1000", {pth + "/Dilepton_/ttH_tttt_m1000/" : bsm4t})
#Ana.Event = Event
#Ana.EventCache = True
##Ana.EventStop = 1000
#Ana.PurgeCache = False
#Ana.Launch
#
#Ana = Analysis()
#Ana.ProjectName = "Project"
#Ana.InputSample("ttbar", {pth + "/Dilepton/ttbar/" : ttbar})
#Ana.Event = Event
#Ana.EventCache = True
##Ana.EventStop = 100
#Ana.Launch
#
#Ana = Analysis()
#Ana.ProjectName = "Project"
#Ana.InputSample("bsm-1000")
#Ana.InputSample("ttbar")
#Ana.EventGraph = modes[mode]
#Ana.DataCache = True
#ApplyFeatures(Ana)
#Ana.Launch

#Ana = Analysis()
#Ana.ProjectName = "Project"
#Ana.InputSample("bsm-1000")
#Ana.InputSample("ttbar")
#Ana.DataCache = True
#Ana.kFolds = 10
#Ana.TrainingSize = 90
#Ana.TrainingName = "k10"
#Ana.Launch

Ana = Analysis()
Ana.ProjectName = "Project"
Ana.TrainingName = "k10"
Ana.Device = "cuda"
Ana.kFold = 1
Ana.Epochs = 100
Ana.BatchSize = 20
Ana.ContinueTraining = False
Ana.Optimizer = "ADAM"
Ana.OptimizerParams = {"lr": 1e-3, "weight_decay": 1e-3}
Ana.Model = RecursiveGraphNeuralNetwork
Ana.DebugMode = False
Ana.EnableReconstruction = False
Ana.Launch
