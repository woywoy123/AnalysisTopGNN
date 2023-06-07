from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.Events import EventGraphTruthJetLepton
from Templates.EventFeatureTemplate import ApplyFeatures
from AnalysisTopGNN.Tools import Tools

smpl = "./TestCaseFiles/Sample/"
Files = {smpl + "Sample1" : ["smpl1.root"], smpl + "Sample2" : ["smpl1.root", "smpl2.root", "smpl3.root"]}

def test_random_sampling():
    lst = list(Files)

    Ana = Analysis()
    Ana.ProjectName = "RandomSampler"
    Ana.InputSample("SingleTop", {lst[0] : Files[lst[0]]})
    Ana.InputSample("4Tops", {lst[1] : Files[lst[1]]})
    Ana.Event = Event
    Ana.EventGraph = EventGraphTruthJetLepton
    Ana.EventStop = 10
    Ana.EventCache = False
    Ana.DataCache = True
    Ana.DumpHDF5 = True
    ApplyFeatures(Ana, "TruthJets")
    Ana.Launch()

    Ana = Analysis()
    Ana.ProjectName = "RandomSampler"
    Ana.InputSample("SingleTop")
    Ana.InputSample("4Tops")
    Ana.DataCache = True
    Ana.TrainingPercentage = 50
    Ana.TrainingSampleName = "Test"
    Ana.Launch()
    Ana.rm("RandomSampler")

def test_merge_data():
    x1 = {"All" : [2], "a" : 1, "b" : {"test1" : 0}}
    x2 = {"All" : [1], "a" : 2, "b" : {"test2" : 0}}
    x_t = {"All" : [2, 1], "a" : 3, "b" : {"test1" : 0, "test2" : 0}}
    T = Tools()
    out = T.MergeData(x1, x2)
    assert out == x_t 

    x1 = {"a" : 1, "b" : {"test1" : 0}}
    x2 = {"All" : [1], "a" : 2, "b" : {"test2" : 0}}
    x_t = {"All" : [1], "a" : 3, "b" : {"test1" : 0, "test2" : 0}}
    out = T.MergeData(x1, x2)
    assert x_t == out
