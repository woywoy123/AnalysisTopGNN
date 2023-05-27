from AnalysisG.Generators import RandomSamplers
from AnalysisG import Analysis
from AnalysisG.Events import Event, GraphChildren
from AnalysisG.Templates import ApplyFeatures
from AnalysisG.Templates import FeatureAnalysis
from AnalysisG.Generators import Optimizer

root1 = "./samples/sample1/smpl1.root"

def test_random_sampling():
    Ana = Analysis()
    Ana.Project = "Project_ML"
    Ana.InputSample(None, root1)
    Ana.Event = Event
    Ana.EventGraph = GraphChildren
    ApplyFeatures(Ana, "TruthChildren")
    Ana.Launch
   
    smpls = Ana.todict
    r = RandomSamplers()
    x = r.RandomizeEvents(smpls, 74)
    assert len(x) == len(smpls)
    
    x = r.MakeTrainingSample(smpls) 

    for i in x["train_hashes"]: assert "train" == smpls[i].TrainMode
    for i in x["test_hashes"]: assert "test" == smpls[i].TrainMode
    
    x = r.MakekFolds(smpls, 10)  
    train = {"k-" + str(i+1) : [] for i in range(10)}
    for f in x:
        for smpl in x[f]["train"]: train[f] += [smpl.hash]
        for smpl in x[f]["leave-out"]: assert smpl.hash not in train[f] 
    
    x = r.MakeDataLoader(smpls, SortByNodes = True)
    assert 12 in x
    assert 13 in x
    assert 14 in x

    x = r.MakeDataLoader(smpls)
    assert "all" in x
    assert len(x["all"]) == len(Ana)
    Ana.rm("Project_ML")

def test_feature_analysis():
    Ana = Analysis()
    Ana.ProjectName = "TestFeature"
    Ana.InputSample(None, root1)
    Ana.Event = Event
    Ana.EventGraph = GraphChildren 
    ApplyFeatures(Ana, "TruthChildren")
    Ana.nEvents = 10
    Ana.TestFeatures = True
    assert Ana.Launch

    def fx(a): return a.NotAFeature

    Ana = Analysis()
    Ana.ProjectName = "TestFeature"
    Ana.InputSample(None, root1)
    Ana.Event = Event
    Ana.EventGraph = GraphChildren 
    ApplyFeatures(Ana, "TruthChildren")
    Ana.nEvents = 10
    Ana.TestFeatures = True
    Ana.AddGraphTruth(fx, "NotAFeature")
    assert Ana.Launch == False

    Ana.rm("TestFeature")


def test_optimizer():
    from models.CheatModel import CheatModel
    Ana = Analysis()
    Ana.InputSample(None, root1)
    Ana.Event = Event
    Ana.ProjectName = "TestOptimizer"
    Ana.EventGraph = GraphChildren 
    ApplyFeatures(Ana, "TruthChildren")
    Ana.EventStop = 100
    Ana.kFolds = 4
    Ana.DataCache = True
    Ana.PurgeCache = True
    Ana.Launch

    op = Optimizer(Ana)
    op.ProjectName = "TestOptimizer"
    op.Model = CheatModel
    op.Device = "cuda"
    op.Optimizer = "ADAM"
    op.OptimizerParams = {"lr" : 0.001}
    op.ContinueTraining = False
    op.EnableReconstruction = True
    op.Batch = 1
    op.Epochs = 20
    op.Launch
   
    op.rm("TestOptimizer") 

def test_optimizer_analysis():
    from models.CheatModel import CheatModel
    Ana = Analysis()
    Ana.InputSample(None, root1)
    Ana.ProjectName = "TestOptimizerAnalysis"
    Ana.Event = Event
    Ana.EventGraph = GraphChildren
    ApplyFeatures(Ana, "TruthChildren")
    Ana.DataCache = True 
    Ana.kFolds = 2
    Ana.kFold = 1
    Ana.Epochs = 20
    Ana.Optimizer = "ADAM"
    Ana.RunName = "RUN"
    Ana.DebugMode = True
    Ana.OptimizerParams = {"lr" : 0.001}
    Ana.Scheduler = "ExponentialLR"
    Ana.ContinueTraining = False
    Ana.SchedulerParams = {"gamma" : 1}
    Ana.Device = "cuda"
    Ana.Model = CheatModel
    Ana.EnableReconstruction = True 
    Ana.BatchSize = 1
    Ana.Launch
    Ana.rm("TestOptimizerAnalysis")

if __name__ == "__main__":
    #test_random_sampling()
    #test_feature_analysis()
    #test_optimizer()
    #test_optimizer_analysis()
    pass
