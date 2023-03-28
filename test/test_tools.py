from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.Events import EventGraphTruthJetLepton
from Templates.EventFeatureTemplate import ApplyFeatures


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
   
