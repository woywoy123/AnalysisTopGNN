from AnalysisG.Events import GraphChildren, GraphTruthJet, GraphDetector
from hyperparams_scan import Opt, sched, btch
from AnalysisG.Templates import ApplyFeatures
from AnalysisG.Submission import Condor
from AnalysisG.Events import Event
from AnalysisG import Analysis
import os

Mode = "TruthJets"
GNN = "BasicGraphNeuralNetwork"
kFolds = 10
Quant = 5
Names = {
    # "other" : "other",
    "t": "t",
    # "tt"    : "tt",
    # "ttbar" : "ttbar",
    # "ttH"   : "ttH",
    # "SM4t"  : "tttt",
    # "ttX"   : "ttX",
    # "ttXll" : "ttXll",
    # "ttXqq" : "ttXqq",
    "ttZ-1000": "ttZ-1000",
    "V": "V",
    # "Vll"   : "Vll",
    # "Vqq"   : "Vqq"
}


if Mode == "TruthChildren":
    gr = GraphChildren
elif Mode == "TruthJets":
    gr = GraphTruthJet
elif Mode == "Jets":
    gr = GraphDetector
else:
    print("failure")
    exit()

if GNN == "BasicGraphNeuralNetwork":
    from BasicGraphNeuralNetwork.model import BasicGraphNeuralNetwork as model
else:
    print("failure")
    exit()


def EventGen(name=None, daod=""):
    pth = os.environ["Samples"] + daod
    Ana = Analysis()
    smpl = Ana.ListFilesInDir(pth, ".root")
    Ana = Ana.Quantize(smpl[pth], Quant)
    out = []
    for i in Ana:
        ana = Analysis()
        ana.Event = Event
        ana.EventCache = True
        ana.chnk = 1000
        ana.Threads = 12
        ana.InputSample(name, {pth: i})
        out.append(ana)
    return out


def DataGen(name=None, daod=""):
    pth = os.environ["Samples"] + daod
    Ana = Analysis()
    smpl = Ana.ListFilesInDir(pth, ".root")
    Ana = Ana.Quantize(smpl[pth], Quant)
    out = []
    for i in Ana:
        ana = Analysis()
        ana.EventGraph = gr
        ana.EventCache = True
        ana.DataCache = True
        ana.chnk = 1000
        ana.Threads = 12
        ana.InputSample(name, {pth: i})
        ApplyFeatures(ana, Mode)
        out.append(ana)
    return out


def Optim(op, op_para, sc, sc_para, batch, k, kF):
    Ana = Analysis()
    Ana.kFold = k
    Ana.kFolds = kF
    Ana.Optimizer = op
    Ana.Scheduler = sc
    Ana.OptimizerParams = op_para
    Ana.SchedulerParams = sc_para
    Ana.EnableReconstruction = True
    Ana.ContinueTraining = True
    Ana.DataCache = True
    Ana.BatchSize = batch
    Ana.Model = model
    Ana.Device = "cuda"
    return Ana


Sub = Condor()
Sub.ProjectName = "Project_" + Mode
Sub.Verbose = 3

all_jbs = []
for name in Names:
    evnt = EventGen(name, Names[name])
    jb_ev_ = "evnt_" + name + "-"
    for k in range(len(evnt)):
        Sub.AddJob(jb_ev_ + str(k), evnt[k], "8GB", "4h")
        all_jbs.append(jb_ev_ + str(k))

all_da = []
for name in Names:
    data = DataGen(name, Names[name])
    jb_da_ = "data_" + name + "-"
    for k in range(len(data)):
        Sub.AddJob(jb_da_ + str(k), data[k], "8GB", "4h", waitfor=all_jbs)
        all_da.append(jb_da_ + str(k))

mrg = Analysis()
mrg.TrainingSize = 90
mrg.kFolds = 10
mrg.DataCache = True
Sub.AddJob("merger", mrg, "8GB", "8h", waitfor=all_da)

op_it, sc_it, b_it = iter(Opt), iter(sched), iter(btch)

for _ in range(len(Opt)):
    n, n_, b_ = next(op_it), next(sc_it), next(b_it)
    name = GNN + "-".join([n, n_, b_])

    op, op_par = Opt[n]
    sc, sc_par = sched[n_]
    b = btch[b_]

    for k in range(kFolds):
        op_ana = Optim(op, op_par, sc, sc_par, b, k + 1, kFolds)
        op_ana.RunName = name
        Sub.AddJob(name + "kF-" + str(k + 1), op_ana, "8GB", "8h", waitfor="merger")

Sub.PythonVenv = "$PythonGNN"
Sub.DumpCondorJobs
