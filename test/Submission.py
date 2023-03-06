from AnalysisTopGNN.Events import EventGraphTruthTopChildren, Event
from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Submission import Condor
from Templates.EventFeatureTemplate import ApplyFeatures
from ExampleModel.BasicBaseLine import BasicBaseLineRecursion
from ExampleModel.CheatModel import CheatModel


def TestSequence():
    x = {
            'tSel': ['t'], 
            'ttbarSel': ['ttbar'], 
            'ttttSel': ['tttt'], 
            't': [], 
            'tttt': [], 
            'ttbar': [], 
            'Merged': ['tSel', 'ttbarSel', 'ttttSel']
        }
    def Recursion(inpt, key = None, start = None):
        if key == None and start == None:
            out = {}
            for i in inpt:
                out[i] = [k for k in Recursion(inpt[i], i, inpt).split("<-") if k != i]
            return out
        if len(inpt) == 0:
            return key
        for i in inpt:
            key += "<-" + Recursion(start[i], i, start)
        return key 

    Recursion(x)
    
    return True


def TestAnalysis(GeneralDir):

    def Test(ev):
        return int(len(ev.TruthTops) == 4)

    def EventGen(Dir, Name):
        Ana = Analysis()
        Ana.ProjectName = "TMPProject"
        Ana.InputSample(Name, Dir)
        Ana.EventCache = True
        Ana.Event = Event
        Ana.Threads = 3
        Ana.EventStop = 9
        Ana.DumpHDF5 = False
        Ana.DumpPickle = True
        Ana.Launch()
        return Ana

    def DataGen(Name):
        Ana = Analysis()
        Ana.ProjectName = "TMPProject"
        Ana.InputSample(Name)
        Ana.DataCache = True
        Ana.EventGraph = EventGraphTruthTopChildren
        Ana.AddGraphFeature(Test)
        Ana.Threads = 10
        Ana.EventStop = None
        Ana.DumpHDF5 = True
        Ana.DumpPickle = False
        Ana.Launch()
        return Ana
    
    ev = EventGen(GeneralDir + "/t", "SingleTop")
    ev += EventGen(GeneralDir + "/ttbar", "ttbar")
    ev += EventGen(GeneralDir + "/tttt", "Signal")
    ev += EventGen([GeneralDir + "/t", GeneralDir + "/ttbar"], "Combined")
    
    gr = DataGen("SingleTop")
    gr += DataGen("ttbar")
    gr += DataGen("Signal")
        
    Objects0 = {}
    for i in ev:
        Objects0[i.Filename] = i
    
    Objects1 = {}
    for i in gr:
        Objects1[i.Filename] = i

    print(len(Objects1), len(Objects0))


    for i in Objects0:
        if i not in Objects1:
            print(i, Objects0[i])
            return False
            continue
        del Objects1[i]
        Objects0[i] = True
    
    return len(Objects1) == sum([0 if Objects0[i] else 1 for i in Objects0 ])


def TestCondorDumping(GeneralDir):
    nfs = GeneralDir
    out = "/home/tnom6927/Dokumente/Project/Analysis/bsm4tops-gnn-analysis/AnalysisTopGNN/test"

    T = Condor()
    T.EventCache = True
    T.DataCache = True
    T.OutputDirectory = out
    T.Tree = "nominal"
    T.ProjectName = "TopEvaluation"

    # Job for creating samples
    A1 = Analysis()
    A1.Threads = 4
    A1.chnk = 100
    A1.EventCache = True
    A1.DumpPickle = True
    A1.Event = Event
    A1.InputSample("ttbar", nfs + "ttbar")

    A2 = Analysis()
    A2.Threads = 4
    A2.chnk = 100
    A2.EventCache = True
    A2.DumpPickle = True
    A2.Event = Event
    A2.InputSample("zmumu", nfs + "Zmumu")
 
    A3 = Analysis()
    A3.Threads = 4
    A3.chnk = 100
    A3.EventCache = True
    A3.DumpPickle = True
    A3.Event = Event
    A3.InputSample("t", nfs + "t")
    
    A4 = Analysis()
    A4.Threads = 4
    A4.chnk = 100
    A4.EventCache = True
    A4.DumpPickle = True
    A4.Event = Event
    A4.InputSample("tttt", nfs + "tttt")

    # Job for creating Dataloader
    D1 = Analysis()
    D1.DataCache = True
    D1.DumpHDF5 = True
    D1.Threads = 4
    D1.chnk = 100
    D1.EventGraph = EventGraphTruthTopChildren
    D1.InputSample("t")
    ApplyFeatures(D1, "TruthChildren")

    D2 = Analysis()
    D2.DataCache = True
    D2.DumpHDF5 = True
    D2.Threads = 4
    D2.chnk = 100
    D2.EventGraph = EventGraphTruthTopChildren
    D2.InputSample("zmumu")
    ApplyFeatures(D2, "TruthChildren")

    T2 = Analysis()
    T2.InputSample("zmumu")
    T2.InputSample("t")
    T2.DataCache = True
    T2.TrainingSampleName = "Test"


    Op1 = Analysis()
    Op1.Device = "cuda"
    Op1.Optimizer = {"ADAM" : {"lr" : 0.0001, "weight_decay" : 0.001}}
    Op1.kFolds = 4
    Op1.Epochs = 3
    Op1.BatchSize = 20
    Op1.RunName = "BasicBase"
    Op1.TrainingSampleName = "Test"
    Op1.ContinueTraining = True
    Op1.Model = BasicBaseLineRecursion()


    Op2 = Analysis()
    Op2.Device = "cuda"
    Op2.Optimizer = {"ADAM" : {"lr" : 0.0001, "weight_decay" : 0.001}}
    Op2.kFolds = 4
    Op2.Epochs = 3
    Op2.BatchSize = 20
    Op2.RunName = "BasicBase"
    Op2.TrainingSampleName = "Test"
    Op2.ContinueTraining = True
    Op2.Model = BasicBaseLineRecursion()



    T.AddJob("t", A3, "10GB", "1h")
    #T.AddJob("t_Data", D1, "10GB", "1h", "t")
    #T.AddJob("tttt", A4, "10GB", "1h")
    T.AddJob("Zmumu", A2, "10GB", "1h")
    #T.AddJob("ttbar", A1, "10GB", "1h")

    T.AddJob("tData", D1, "10GB", "1h", ["t", "Zmumu"])
    T.AddJob("DataTraining", T2, "10GB", "1h", ["tData", "ZmumuData"])
    T.AddJob("ZmumuData", D2, "10GB", "1h", ["t", "Zmumu"])
    
    T.AddJob("TrainingBase", Op1, "10GB", "1h", ["DataTraining"])
    T.AddJob("TrainingCheat", Op2, "10GB", "1h", ["DataTraining"])

    #T.LocalDryRun() 
    T.DumpCondorJobs() 
    
    # t -> t_Data (x), tData -> DataTraining
    # t_Data 
    # Zmumu -> tData -> ZmumuData -> DataTraining


    return True

def TestSelectionDumping(GeneralDir):
    nfs = GeneralDir
    out = "/home/tnom6927/Dokumente/Project/Analysis/bsm4tops-gnn-analysis/AnalysisTopGNN/test"

    T = Condor()
    T.EventCache = True
    T.DataCache = True
    T.OutputDirectory = out
    T.Tree = "nominal"
    T.CondaEnv = "GNN"
    T.ProjectName = "TopEvaluation"

    # Job for creating samples
    A1 = Analysis()
    A1.Threads = 4
    A1.chnk = 100
    A1.EventCache = True
    A1.DumpPickle = True
    A1.Event = Event
    A1.InputSample("ttbar", nfs + "ttbar")

    A3 = Analysis()
    A3.Threads = 4
    A3.chnk = 100
    A3.EventCache = True
    A3.DumpPickle = True
    A3.Event = Event
    A3.InputSample("t", nfs + "t")
    
    A4 = Analysis()
    A4.Threads = 4
    A4.chnk = 100
    A4.EventCache = True
    A4.DumpPickle = True
    A4.Event = Event
    A4.InputSample("tttt", nfs + "tttt")
    
    from ExampleSelection import Example2, Example

    D1 = Analysis()
    D1.Threads = 4
    D1.chnk = 100
    D1.Event = Event
    D1.InputSample("t")
    D1.AddSelection("Example", Example)

    D2 = Analysis()
    D2.Threads = 4
    D2.chnk = 100
    D2.Event = Event
    D2.InputSample("ttbar")
    D2.AddSelection("Example", Example)

    D3 = Analysis()
    D3.Threads = 4
    D3.chnk = 100
    D3.Event = Event
    D3.InputSample("tttt")
    D3.AddSelection("Example", Example)

    M1 = Analysis()
    M1.Threads = 4
    M1.chnk = 100
    M1.MergeSelection("Example")


    T.AddJob("tSel", D1, "10GB", "1h", ["t"])
    T.AddJob("ttbarSel", D2, "10GB", "1h", ["ttbar"])
    T.AddJob("ttttSel", D3, "10GB", "1h", ["tttt"])
    
    T.AddJob("Merged", M1, "10GB", "1h", ["tSel", "ttbarSel", "ttttSel"])

    T.AddJob("t", A3, "10GB", "1h")
    T.AddJob("tttt", A4, "10GB", "1h", ["ttbar"])
    T.AddJob("ttbar", A1, "10GB", "1h")
 
    T.DumpCondorJobs() 
    #T.LocalDryRun()

    from AnalysisTopGNN.IO import UnpickleObject
    x = UnpickleObject("./TopEvaluation/Selections/Merged/Example.pkl")
    if x == None:
        return False
    return True 
