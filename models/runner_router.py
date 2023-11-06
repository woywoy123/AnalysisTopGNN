from AnalysisG.Templates import ApplyFeatures
from AnalysisG.Events import *
from AnalysisG.Tools import Tools
from AnalysisG.IO import UpROOT
from AnalysisG import Analysis

from production.BasicBaseLine import BasicBaseLineRecursion
from production.RecursiveGraphNeuralNetwork import RecursiveGraphNeuralNetwork
from production.BasicGraphNeuralNetwork import BasicGraphNeuralNetwork
from Beta.pathnetz import RecursivePathNetz
from Beta.model import MarkovGraphNet

from dataset_mapping import DataSets

models = {
            "RGNN" : RecursiveGraphNeuralNetwork,
            "BBLR" : BasicBaseLineRecursion,
            "BGNN" : BasicGraphNeuralNetwork,
            "RPN" : RecursivePathNetz,
            "MKGN" : MarkovGraphNet
}

graphs = {
            "TruthChildren_All" : GraphChildren,
            "TruthChildren_NoNu" : GraphChildrenNoNu,
            "TruthJets_All" : GraphTruthJet,
            "TruthJets_NoNu": GraphTruthJetNoNu,
            "Jets_All" : GraphJet,
            "Jets_NoNu" : GraphJetNoNu,
            "Jets_Detector" : GraphDetector
}


class Models:

    def __init__(self, model_name):
        self.models = models
        self.model_list = list(models)
        msg = "Model not found. Options are: "
        self._this = None
        try: self._this = self.models[model_name]
        except KeyError: print(msg + "-> \n".join(self.model_list))

class Graphs:

    def __init__(self, graph_name):
        self.graphs = graphs
        self.graph_list = list(graphs)
        msg = "Graph not found. Options are: "
        self._this = None
        try: self._this = self.graphs[graph_name]
        except KeyError: print(msg + "-> \n".join(self.graph_list))


class AnalysisBuild:

    def __init__(self, ProjectName = "Project"):
        self.Analysis = {}
        self.ProjectName = ProjectName
        self.Event = None
        self.Graph = None
        self.DataCache = False
        self.EventCache = False
        self.SamplePath = None
        self.EventStop = None
        self.SampleDict = {}
        self._quantmap = {}
        self._meta = {}
        self._data = DataSets()
        self._jobs = {}

    def AddDatasetName(self, name, n_roots = -1):
        if len(self._meta): pass
        else: self.FetchMeta(n_roots)

        for x, j in self._meta.items():
            name_ = self._data.CheckThis(j.DatasetName)
            msg = "Sample (" + j.DatasetName + ") not indexed in 'dataset_mapping'"
            if name_: pass
            else: print(msg); continue

            if name_ != name: continue

            if name_ in self.SampleDict: pass
            else: self.SampleDict[name_] = []

            if n_roots == -1: pass
            elif len(self.SampleDict[name_]) > n_roots: break
            self.SampleDict[name_].append(x)

        if name in self.SampleDict: return
        print("Sample not indexed")
        exit()

    def FetchMeta(self, n_roots = -1):
        if self.SamplePath is not None: pass
        else: print("Set the 'SamplePath'"); exit()
        x = UpROOT(self.SamplePath)
        if n_roots != -1:
            x.Files = {k : x[: n_roots] for k, x in x.Files.items()}
            ROOTFile = [i + "/" + k for i in x.Files for k in x.Files[i]]
            x.File = {i: None for i in ROOTFile}
        x.metacache_path = "./" + self.ProjectName + "/metacache/"
        x.Trees = ["nominal"]
        x.OnlyMeta = True
        self._meta = x.GetAmiMeta()

    def MakeGraphCache(self, name):
        self.Graph = Graphs(name)._this
        if self.Graph is not None: pass
        else: print("No Graph Implementation"); exit()

        for ana in self.Analysis.values():
            ana.Graph = self.Graph
            ana.EventName = self.Event.__name__
            ApplyFeatures(ana, name.split("_")[0])
            ana.DataCache = True

    def MakeEventCache(self):
        if self.Event is not None: pass
        else: print("Set the 'Event'"); exit()

        this = "E-" + self.Event.__name__
        if this in self.Analysis: pass
        else: self.Analysis[this] = Analysis()
        self.Analysis[this].Event = self.Event
        self.Analysis[this].EventName = self.Event.__name__

    def QuantizeSamples(self, size = 100):
        if self.SamplePath is not None: pass
        else: print("Set the 'SamplePath'"); exit()
        t = Tools()
        for i, rt in self.SampleDict.items():
            lst = list(t.Quantize(rt, size))
            smpls = {}
            for index, j in zip(range(len(lst)), lst): smpls[i + "_" + str(index)] = j
            self._quantmap.update(smpls)

    def TrainingSample(self, train_name, training_size = 90):
        x = "T-" + train_name
        if x in self.Analysis: return
        self.Analysis[x] = Analysis()
        self.Analysis[x].TrainingName = train_name
        self.Analysis[x].TrainingSize = training_size
        self.Analysis[x].EventStop = self.EventStop
        self.Analysis[x].DataCache = True
        self.Analysis[x].kFolds = 10
        self.Analysis[x].GraphName = self.Graph.__name__

    def ModelTrainer(self, model_name):
        x = Models(model_name)
        if x._this is None: exit()
        return x._this

    def Make(self):
        for ana in self.Analysis:
            if ana.startswith("T-"):
                self._jobs[ana] = Analysis()
                self._jobs[ana].ImportSettings(self.Analysis[ana].ExportSettings())
                self._jobs[ana].ProjectName = self.ProjectName
                self._jobs[ana].InputSample(None)
                continue

            if self.EventCache: self.Analysis[ana].EventCache = True
            if self.DataCache: self.Analysis[ana].DataCache = True
            for i, j in self._quantmap.items():
                self._jobs[ana + "-" + i] = Analysis()
                self._jobs[ana + "-" + i].ImportSettings(self.Analysis[ana].ExportSettings())
                self._jobs[ana + "-" + i].ProjectName = self.ProjectName
                self._jobs[ana + "-" + i].InputSample(i, j)

                if self.EventStop is None: continue
                self._jobs[ana + "-" + i].EventStop = self.EventStop
            if len(self._quantmap): continue
            self._jobs[ana] = Analysis()
            self._jobs[ana].ImportSettings(self.Analysis[ana].ExportSettings())
            self._jobs[ana].EventStop = self.EventStop
            self._jobs[ana].ProjectName = self.ProjectName
            for i, j in self.SampleDict.items(): self._jobs[ana].InputSample(i, j)
        return self._jobs
