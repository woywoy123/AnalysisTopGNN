from AnalysisG.Events import Event, GraphChildren
from AnalysisG.Generators import RandomSamplers
from AnalysisG.Templates import ApplyFeatures
from AnalysisG import Analysis

root1 = "./samples/sample1/smpl1.root"

def test_random_sampling():
    Ana = Analysis()
    Ana.ProjectName = "Project_ML"
    Ana.Event = Event
    Ana.Graph = GraphChildren
    Ana.InputSample(None, root1)
    ApplyFeatures(Ana, "TruthChildren")
    Ana.Launch()

    Ana.GetAll = True
    smpls = Ana.makelist()
    Ana.GetAll = False
    r = RandomSamplers()
    r_ = r.RandomizeEvents(smpls, len(smpls))
    assert len(r_) == len(smpls)

    x = r.MakeTrainingSample(smpls)
    for i in x["train_hashes"]: assert r_[i].Train
    for i in x["test_hashes"]:  assert r_[i].Eval

    x = r.MakekFolds(smpls, 10)
    train = {"k-" + str(i + 1): [] for i in range(10)}
    for f in x:
        for smpl in x[f]["train"]: train[f] += [smpl.hash]
        for smpl in x[f]["leave-out"]:
            assert smpl.hash not in train[f]

    x = r.MakeDataLoader(smpls, SortByNodes=True)
    nodes = {}
    for smpl in [t[0] for t in x]:
        ev = Ana[smpl].num_nodes.item()
        if ev not in nodes: nodes[ev] = 0
        nodes[ev] += 1
    assert 12 in nodes
    assert 13 in nodes
    assert 14 in nodes

    x = r.MakeDataLoader(smpls)
    Ana.EventName = None
    assert sum(nodes.values()) == len(Ana)
    Ana.rm("Project_ML")

def fx(a): return a.NotAFeature

def test_feature_analysis():
    Ana = Analysis()
    Ana.ProjectName = "Project_ML"
    Ana.InputSample(None, root1)
    Ana.Event = Event
    Ana.Graph = GraphChildren
    ApplyFeatures(Ana, "TruthChildren")
    Ana.nEvents = 10
    Ana.TestFeatures = True
    Ana.Launch()

    Ana = Analysis()
    Ana.ProjectName = "TestFeature"
    Ana.InputSample(None, root1)
    Ana.Event = Event
    Ana.Graph = GraphChildren
    ApplyFeatures(Ana, "TruthChildren")
    Ana.nEvents = 10
    Ana.TestFeatures = True
    Ana.AddGraphTruthFeature(fx, "NotAFeature")
    Ana.Launch()
    Ana.rm("Project_ML")
    Ana.rm("TestFeature")

def test_optimizer():
    from models.CheatModel import CheatModel

    Ana = Analysis()
    Ana.InputSample(None, root1)
    Ana.ProjectName = "Project_ML"
    Ana.Event = Event
    Ana.Chunks = 10000
    Ana.EventCache = True
    Ana.Launch()

    AnaG = Analysis()
    AnaG.ProjectName = "Project_ML"
    AnaG.Graph = GraphChildren
    AnaG.Chunks = 1000
    ApplyFeatures(AnaG, "TruthChildren")
    AnaG.Launch()
    AnaG.GetAll = True
    for i in AnaG:
        assert i.Graph
        assert i.N_eta is not None


    AnaG = Analysis()
    AnaG.ProjectName = "Project_ML"
    AnaG.TrainingSize = 90
    AnaG.kFolds = 10
    AnaG.Launch()

if __name__ == "__main__":
    test_random_sampling()
    test_feature_analysis()
    test_optimizer()
