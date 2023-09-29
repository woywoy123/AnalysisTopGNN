from AnalysisG import Analysis
from AnalysisG.Events import Event, GraphChildren
from examples.Event import EventEx
from examples.Graph import DataGraph
from examples.ExampleSelection import Example, Example2
from AnalysisG.Templates import ApplyFeatures
from models.CheatModel import CheatModel
from AnalysisG.IO import UnpickleObject

from AnalysisG.Submission import Condor
from conftest import clean_dir

smpl = "./samples/"
Files = {
    smpl + "sample1": ["smpl1.root"],
    smpl + "sample2": ["smpl1.root", "smpl2.root", "smpl3.root"],
}


def _template(default=True):
    AnaE = Analysis()
    AnaE.ProjectName = "Project"
    if default == True:
        AnaE.InputSample("Sample1", smpl + "sample1/" + Files[smpl + "sample1"][0])
        AnaE.InputSample("Sample2", smpl + "sample2/" + Files[smpl + "sample2"][1])
    else:
        AnaE.InputSample(**default)
    AnaE.Threads = 2
    AnaE.Verbose = 1
    return AnaE


def test_dumping_events():
    Ana = _template()
    Ana.Event = EventEx()

    con = Condor()
    con.EventCache = True
    con.PythonVenv = "$PythonGNN"
    con.ProjectName = "Project"
    con.AddJob("example", Ana)
    con.DumpCondorJobs()
    con.TestCondorShell()
    Ana2 = _template()
    Ana2.EventCache = True
    x = []
    for i in Ana2: x.append(i.hash)
    assert len(x) != 0
    clean_dir()

def Feat(a):
    return 1

def test_dumping_graphs():
    Ana = _template()
    Ana.EventGraph = DataGraph
    Ana.DataCache = True
    Ana.AddGraphFeature(Feat)

    con = Condor()
    con.PythonVenv = "$PythonGNN"
    con.ProjectName = "Project"
    con.AddJob("Data", Ana, waitfor=["Events"])

    Ana = _template()
    Ana.Event = EventEx
    Ana.EventCache = True
    con.AddJob("Events", Ana)

    con.DumpCondorJobs()
    con.TestCondorShell()

    Ana = _template()
    Ana.DataCache = True
    x = []
    for i in Ana: x.append(i.hash)
    assert len(x) != 0
    clean_dir()


def test_dumping_event_selection():
    con = Condor()
    con.rm("./Project")
    con.PythonVenv = "$PythonGNN"
    con.ProjectName = "Project"

    Ana_1 = _template(
        {"Name": "smpl1", "SampleDirectory": {smpl + "sample2": ["smpl1.root"]}}
    )
    Ana_1.Event = EventEx
    Ana_1.EventCache = True

    Ana_2 = _template(
        {"Name": "smpl2", "SampleDirectory": {smpl + "sample2": ["smpl2.root"]}}
    )
    Ana_2.Event = EventEx
    Ana_2.EventCache = True

    Ana_3 = _template(
        {"Name": "smpl3", "SampleDirectory": {smpl + "sample2": ["smpl3.root"]}}
    )
    Ana_3.Event = EventEx
    Ana_3.EventCache = True

    con.AddJob("smpl1", Ana_1)
    con.AddJob("smpl2", Ana_2)
    con.AddJob("smpl3", Ana_3)

    Ana_s1 = _template({"Name": "smpl1"})
    Ana_s1.AddSelection("example1", Example)
    con.AddJob("example1_1", Ana_s1, waitfor=["smpl1", "smpl2", "smpl3"])

    Ana_s2 = _template({"Name": "smpl2"})
    Ana_s2.AddSelection("example1", Example)
    con.AddJob("example1_2", Ana_s2, waitfor=["smpl1", "smpl2", "smpl3"])

    Ana_s3 = _template({"Name": "smpl3"})
    Ana_s3.AddSelection("example1", Example)
    con.AddJob("example1_3", Ana_s3, waitfor=["smpl1", "smpl2", "smpl3"])

    Ana_sum = Analysis()
    Ana_sum.ProjectName = "Project"
    Ana_sum.MergeSelection("example1")

    con.AddJob("sum", Ana_sum, waitfor=["example1_1", "example1_2", "example1_3"])
    con.DumpCondorJobs()
    con.TestCondorShell()

    Ana_T = _template({"Name": "smpl1"})
    Ana_T.InputSample("smpl2")
    Ana_T.InputSample("smpl3")
    Ana_T.ProjectName = "Project"
    Ana_T.Event = EventEx
    Ana_T.Launch
    clean_dir()


def test_dumping_optimization():
    con = Condor()
    con.PythonVenv = "$PythonGNN"
    con.ProjectName = "Project"

    Ana_1 = _template(
        {"Name": "smpl1", "SampleDirectory": {smpl + "sample2": ["smpl1.root"]}}
    )
    Ana_1.Event = Event
    Ana_1.EventCache = True

    Ana_2 = _template(
        {"Name": "smpl2", "SampleDirectory": {smpl + "sample2": ["smpl2.root"]}}
    )
    Ana_2.Event = Event
    Ana_2.EventCache = True

    Ana_3 = _template(
        {"Name": "smpl3", "SampleDirectory": {smpl + "sample2": ["smpl3.root"]}}
    )
    Ana_3.Event = Event
    Ana_3.EventCache = True

    con.AddJob("smpl1", Ana_1)
    con.AddJob("smpl2", Ana_2)
    con.AddJob("smpl3", Ana_3)

    AnaD_1 = _template({"Name": "smpl1"})
    ApplyFeatures(AnaD_1, "TruthChildren")
    AnaD_1.DataCache = True
    AnaD_1.EventGraph = GraphChildren

    AnaD_2 = _template({"Name": "smpl2"})
    ApplyFeatures(AnaD_2, "TruthChildren")
    AnaD_2.DataCache = True
    AnaD_2.EventGraph = GraphChildren

    AnaD_3 = _template({"Name": "smpl3"})
    ApplyFeatures(AnaD_3, "TruthChildren")
    AnaD_3.DataCache = True
    AnaD_3.EventGraph = GraphChildren

    con.AddJob("Dsmpl1", AnaD_1, waitfor=["smpl1"])
    con.AddJob("Dsmpl2", AnaD_2, waitfor=["smpl2"])
    con.AddJob("Dsmpl3", AnaD_3, waitfor=["smpl3"])

    AnaOp = _template({"Name": "smpl1"})
    AnaOp.InputSample(**{"Name": "smpl2"})
    AnaOp.InputSample(**{"Name": "smpl3"})
    AnaOp.RunName = "run-1"
    AnaOp.DataCache = True
    AnaOp.kFolds = 4
    AnaOp.Epochs = 10
    AnaOp.Optimizer = "ADAM"
    AnaOp.Scheduler = "ExponentialLR"
    AnaOp.OptimizerParams = {"lr": 0.001}
    AnaOp.SchedulerParams = {"gamma": 1}
    AnaOp.Device = "cuda"
    AnaOp.BatchSize = 2
    AnaOp.Model = CheatModel
    AnaOp.DebugMode = True
    AnaOp.EnableReconstruction = True

    con.AddJob("run-1", AnaOp, waitfor=["Dsmpl1", "Dsmpl2", "Dsmpl3"])
    con.DumpCondorJobs()
    con.TestCondorShell()
    clean_dir()

if __name__ == "__main__":
    test_dumping_events()
    test_dumping_graphs()
    test_dumping_event_selection()
    test_dumping_optimization()
