from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.Events import EventGraphTruthJetLepton
from Templates.EventFeatureTemplate import ApplyFeatures

def TestRandomSampling(Files):

    Ana = Analysis()
    Ana.ProjectName = "RandomSampler"
    Ana.InputSample("SingleTop", Files[0])
    Ana.InputSample("4Tops", Files[1])
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
    
    return True
