from runner_router import AnalysisBuild, Graphs
from AnalysisG.Events import Event
from AnalysisG import Analysis
from AnalysisG.Tools import Code
import os

mode = "Jets_Detector"
name = "Example" #"Project_ML"
model = "RPN"

#"TruthChildren_All" : GraphChildren,
#"TruthChildren_NoNu" : GraphChildrenNoNu,
#"TruthJets_All" : GraphTruthJet,
#"TruthJets_NoNu": GraphTruthJetNoNu,
#"Jets_All" : GraphJet,
#"Jets_NoNu" : GraphJetNoNu,
#"Jets_Detector" : GraphDetector

# ----- candidates ----- #
#"RPN"  : RecursivePathNetz,


#"RGNN" : RecursiveGraphNeuralNetwork, 
#"BBLR" : BasicBaseLineRecursion,
#"BGGN" : BasicGraphNeuralNetwork,
#"MKGN" : MarkovGraphNet <--- need to fix

auto = AnalysisBuild(name)
if False:
    auto.SamplePath = os.environ["Samples"]
    auto.AddDatasetName("ttH-m1000")
    auto.AddDatasetName("ttbar")
    auto.AddDatasetName("tttt (SM)")
    auto.AddDatasetName("ttH")
    auto.Event = Event
    auto.EventCache = True
    auto.MakeEventCache()
    auto.MakeGraphCache(mode)
    auto.QuantizeSamples(100)
    auto.TrainingSample("sample-detector", 90)
    #auto.EventStop = 10000
    for i, job in auto.Make().items():
        job.Threads = 22
        job.Chunks = 1000
        print("-> " + i)
        job.Launch()
        del job

Ana = Analysis()
Ana.ProjectName = name
Ana.Device = "cuda"
Ana.TrainingName = "sample-detector"
Ana.Model = auto.ModelTrainer(model)
Ana.kFold = 10
Ana.Epochs = 100
Ana.BatchSize = 1
Ana.MaxGPU = 20
Ana.MaxRAM = 200
Ana.RunName = model + "-" + mode
Ana.Optimizer = "ADAM"
Ana.EventName = None
Ana.GraphName = "GraphDetector"
Ana.Tree = "nominal"
Ana.OptimizerParams = {"lr": 1e-4, "weight_decay": 1e-6}
Ana.PlotLearningMetrics = True
Ana.ContinueTraining = False
Ana.DebugMode = False
Ana.KinematicMap = {
                "top_edge" : "polar -> N_pT, N_eta, N_phi, N_energy",
                "res_edge" : "polar -> N_pT, N_eta, N_phi, N_energy"
}
Ana.Launch()


