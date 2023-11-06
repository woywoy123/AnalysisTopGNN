from AnalysisG.Generators import RandomSamplers, Optimizer
from AnalysisG.Events import Event, GraphChildren
from AnalysisG.Templates import ApplyFeatures
from AnalysisG import Analysis

root1 = "./samples/sample1/smpl1.root"

def test_random_sampling():
    Ana = Analysis()
    Ana.rm("Project_ML")
    Ana.ProjectName = "Project_ML"
    Ana.Event = Event
    Ana.Graph = GraphChildren
    Ana.InputSample(None, root1)
    ApplyFeatures(Ana, "TruthChildren")
    Ana.Launch()
    Ana.GetGraph = True
    smpls = Ana.makelist()
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
    assert sum(nodes.values()) == Ana.ShowLength["nominal/GraphChildren"]
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
    from AnalysisG._cmodules.cWrapping import ModelWrapper
    from models.CheatModel import CheatModel
    from torch_geometric.data import Batch
    from AnalysisG.Model import Model

    Ana = Analysis()
    Ana.InputSample(None, root1)
    Ana.ProjectName = "Project_ML"
    Ana.Event = Event
    Ana.Chunks = 1000
    Ana.EventCache = True
    Ana.Launch()

    AnaG = Analysis()
    AnaG.ProjectName = "Project_ML"
    AnaG.EventName = "Event"
    AnaG.Graph = GraphChildren
    AnaG.Chunks = 1000
    ApplyFeatures(AnaG, "TruthChildren")
    AnaG.DataCache = True
    AnaG.Launch()
    x = []
    for i in AnaG:
        assert i.Graph
        assert i.N_eta is not None
        x.append(i)
    assert len(x)

    AnaG = Analysis()
    AnaG.ProjectName = "Project_ML"
    AnaG.EventCache = False
    AnaG.DataCache = True
    AnaG.TrainingSize = 90
    AnaG.GraphName = "GraphChildren"
    AnaG.kFolds = 10
    AnaG.Launch()

    AnaG = Analysis()
    AnaG.ProjectName = "Project_ML"
    AnaG.TrainingName = "untitled"
    AnaG.GraphName = "GraphChildren"
    AnaG.DataCache = True
    mod = ModelWrapper()
    mod.__params__ = {"test" : "here"}
    mod.model = CheatModel

    wrp_broken = Model(CheatModel)
    wrp_ok = Model(CheatModel)
    wrp_ok.__params__ = {"test" : "here"}
    for i in AnaG:
        x = Batch().from_data_list([i.release_graph().to("cpu")])
        mod.match_data_model_vars(x)
        assert "i" in mod.in_map
        assert "edge_index" in mod.in_map
        assert "N_pT" in mod.in_map
        assert "N_eta" in mod.in_map
        assert "N_energy" in mod.in_map
        assert "E_T_top_edge" in mod.in_map
        assert "O_top_edge" == mod.out_map["E_T_top_edge"]
        assert "top_edge" in mod.loss_map
        assert mod.model.test == "here"

        t = mod(x)
        assert len(t["graphs"]) == 1
        assert "total" in t
        assert "L_top_edge" in t
        assert "A_top_edge" in t

        assert not wrp_broken.SampleCompatibility(x)
        wrp_ok.SampleCompatibility(x)
        assert "i" in wrp_ok.in_map
        assert "edge_index" in wrp_ok.in_map
        assert "N_pT" in wrp_ok.in_map
        assert "N_eta" in wrp_ok.in_map
        assert "N_energy" in wrp_ok.in_map
        assert "E_T_top_edge" in wrp_ok.in_map
        assert "O_top_edge" == wrp_ok.out_map["E_T_top_edge"]
        assert "top_edge" in wrp_ok.loss_map
        assert wrp_ok.model.test == "here"
        t = wrp_ok(x)
        assert len(t["graphs"]) == 1
        assert "total" in t
        assert "L_top_edge" in t
        assert "A_top_edge" in t
        break

    AnaG = Analysis()
    AnaG.ProjectName = "Project_ML"
    AnaG.TrainingName = "untitled"
    AnaG.Device = "cuda"
    AnaG.ContinueTraining = False
    AnaG.DataCache = True
    AnaG.DebugMode = True
    AnaG.Model = CheatModel
    AnaG.PlotLearningMetrics = False
    AnaG.ModelParams = {"test" : "here"}
    AnaG.Optimizer = "ADAM"
    AnaG.OptimizerParams = {"lr" : 0.001}
    AnaG.kFold = [1, 2]
    AnaG.BatchSize = 3
    AnaG.Epochs = 20
    AnaG.Device = "cpu"
    AnaG.GraphName = "GraphChildren"
    AnaG.Tree = "nominal"
    AnaG.RestoreTracer()

    op = Optimizer()
    op.Start(AnaG)
    op.rm("Project_ML")

def test_optimizer_analysis():
    from models.CheatModel import CheatModel

    Ana = Analysis()
    Ana.InputSample(None, root1)
    Ana.ProjectName = "Project_ML"
    ApplyFeatures(Ana, "TruthChildren")
    Ana.Event = Event
    Ana.Graph = GraphChildren
    Ana.DataCache = True
    Ana.Epochs = 20
    Ana.Optimizer = "ADAM"
    Ana.RunName = "RUN"
    Ana.ModelParams = {"test" : "here"}
    Ana.DebugMode = True
    Ana.OptimizerParams = {"lr": 0.001}
    Ana.Scheduler = "ExponentialLR"
    Ana.ContinueTraining = False
    Ana.SchedulerParams = {"gamma": 1}
    Ana.Device = "cpu"
    Ana.Model = CheatModel
    Ana.PlotLearningMetrics = True
    Ana.BatchSize = 1
    Ana.Launch()
    Ana.rm("Project_ML")



def test_parallel_analysis():
    from models.CheatModel import CheatModel

    Ana = Analysis()
    Ana.rm("Project")
    Ana.ProjectName = "Project"
    Ana.InputSample(None, root1)
    Ana.Event = Event
    Ana.Graph = GraphChildren
    ApplyFeatures(Ana, "TruthChildren")
    Ana.DataCache = True
    Ana.Launch()

    Ana = Analysis()
    Ana.ProjectName = "Project"
    Ana.DataCache = True
    Ana.GraphName = "GraphChildren"
    Ana.TrainingSize = 50
    Ana.kFolds = 10
    Ana.Launch()

    Ana = Analysis()
    Ana.ProjectName = "Project"
    Ana.Epochs = 5
    Ana.kFold = [1, 2]
    Ana.Optimizer = "ADAM"
    Ana.OptimizerParams = {"lr": 0.001}
    Ana.Device = "cpu"
    Ana.GraphName = "GraphChildren"
    Ana.Model = CheatModel
    Ana.ModelParams = {"test" : "here"}
    Ana.ContinueTraining = True
    Ana.BatchSize = 1
    Ana.Launch()

    Ana = Analysis()
    Ana.ProjectName = "Project"
    Ana.Epochs = 5
    Ana.kFold = [1]
    Ana.GraphName = "GraphChildren"
    Ana.ContinueTraining = True
    Ana.Optimizer = "ADAM"
    Ana.ModelParams = {"test" : "here"}
    Ana.OptimizerParams = {"lr": 0.001}
    Ana.Device = "cpu"
    Ana.Model = CheatModel
    Ana.BatchSize = 1
    Ana.Launch()

    Ana.rm("Project")



def test_plotting_analysis():
    from models.CheatModel import CheatModel

    Ana = Analysis()
    Ana.ProjectName = "Project"
    Ana.InputSample(None, root1)
    Ana.Event = Event
    Ana.Graph = GraphChildren
    ApplyFeatures(Ana)
    Ana.DataCache = True
    Ana.Launch()

    Ana = Analysis()
    Ana.ProjectName = "Project"
    Ana.DataCache = True
    Ana.Event = None
    Ana.GraphName = "GraphChildren"
    Ana.TrainingSize = 50
    Ana.kFolds = 10
    Ana.Launch()

    Ana = Analysis()
    Ana.ProjectName = "Project"
    Ana.Epochs = 2
    Ana.kFold = 1
    Ana.GraphName = "GraphChildren"
    Ana.ContinueTraining = False
    Ana.PlotLearningMetrics = True
    Ana.Optimizer = "ADAM"
    Ana.ModelParams = {"test" : "here"}
    Ana.OptimizerParams = {"lr": 0.001}
    Ana.Device = "cpu"
    Ana.Model = CheatModel
    Ana.BatchSize = 1
    Ana.KinematicMap = {"top_edge" : "polar -> N_pT, N_eta, N_phi, N_energy"}
    Ana.Launch()
    Ana.rm("Project")


if __name__ == "__main__":
    test_random_sampling()
    test_feature_analysis()
    test_optimizer()
    test_optimizer_analysis()
    test_parallel_analysis()
    test_plotting_analysis()
