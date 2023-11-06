from AnalysisG.Generators.SelectionGenerator import SelectionGenerator
from AnalysisG.Generators.SampleGenerator import RandomSamplers
from AnalysisG.Generators.EventGenerator import EventGenerator
from AnalysisG.Generators.GraphGenerator import GraphGenerator
from AnalysisG._cmodules.ctools import cCheckDifference
from AnalysisG.Generators.Interfaces import _Interface
from AnalysisG.Generators.Optimizer import Optimizer
from AnalysisG.Templates import FeatureAnalysis
from AnalysisG.SampleTracer import SampleTracer
from AnalysisG.Notification import _Analysis
from typing import Union

def search(x):
    f = {}
    f["SampleName"] = False
    f["Files"] = []
    f["get"] = {}

    f["SampleName"] = x.SampleName in x
    try: f["Files"] = x.SampleMap[x.SampleName]
    except KeyError: pass

    for i in f["Files"]:
        x.GetAll = True
        i = x.abs(i).split("/")
        file, path = i[-1], "/".join(i[:-1])
        if path not in f["get"]: f["get"][path] = []
        f["get"][path].append(file)
    x.GetAll = True
    f.update(x.makehashes())
    x.GetAll = False
    x._get = f

class Analysis(_Analysis, SampleTracer, _Interface):
    def __init__(
        self,
        SampleDirectory: Union[str, dict, list, None] = None,
        Name: Union[str] = None,
    ):
        SampleTracer.__init__(self)
        self.Caller = "ANALYSIS"
        _Analysis.__init__(self)
        _Interface.__init__(self)
        self.PurgeCache = False
        self.TestFeatures = False
        self.triggered = False
        self.SampleName = ""
        self.nEvents = 10
        self._get = {}

        if Name is None and SampleDirectory is None: return
        self.InputSample(Name, SampleDirectory)

    def __build__(self):
        self.StartingAnalysis()
        self._BuildingCache()
        if self.PurgeCache: self._WarningPurge()
        self.triggered = True


    def __FeatureAnalysis__(self):
        if self.Graph is None: return True
        if not self.TestFeatures: return

        tests = [i for i in self]
        if len(tests) < self.nEvents: tests
        else: tests = tests[:self.nEvents]

        code_ = self.Graph.code
        code  = code_["__state__"]

        f = FeatureAnalysis()
        f.Verbose = self.Verbose
        for gr, i in code["graph_feature"].items():
            gr, i = gr.decode("UTF-8")[4:], i.decode("UTF-8")
            f.GraphAttribute[gr] = code_[i]

        for no, i in code["node_feature"].items():
            no, i = no.decode("UTF-8")[4:], i.decode("UTF-8")
            f.NodeAttribute[no] = code_[i]

        for ed, i in code["edge_feature"].items():
            ed, i = ed.decode("UTF-8")[4:], i.decode("UTF-8")
            f.EdgeAttribute[ed] = code_[i]

        return f.TestEvent(tests, self.Graph)


    def __RandomSampler__(self):
        if not self.TrainingSize: return
        pth = self.WorkingPath + "Training/DataSets/"
        pth += self.TrainingName

        get = sum(self._get["graph"].values(), [])
        self.RestoreGraphs(get)
        maps = self[self.GraphName]
        if maps: pass
        else: return self.EmptySampleList()
        dic = {}
        for i in maps:
            if i.SkipEvent: continue
            if i.EmptyGraph: continue
            dic[i.hash] = i
        r = RandomSamplers()
        r.ImportSettings(self.ExportSettings())
        if not self.TrainingSize: out = {}
        else: out = r.MakeTrainingSample(dic, self.TrainingSize)
        r.SaveSets(out, pth)

        if not self.kFolds: out = {}
        else: out = r.MakekFolds(dic, self.kFolds, True, True)
        if out == False: return
        r.SaveSets(out, pth)

    def __Selection__(self):
        if len(self.Selections): pass
        elif len(self.SelectionName): pass
        else: return

        get = sum(self._get["selection"].values(), [])
        get_ev = sum(self._get["event"].values(), [])
        c = cCheckDifference(get_ev, get, self.Threads)
        if len(get) and self.GetSelection: self.RestoreSelections(get)
        elif not len(get): pass
        elif len(c): self.RestoreEvents(c)

        if len(self.Selections): pass
        else: return

        if self.Tree: pass
        elif not len(self.ShowTrees): return
        elif len(self.ShowTrees) > 1: return
        else: self.Tree = self.ShowTrees[0]


        sel = SelectionGenerator()
        sel.ImportSettings(self.ExportSettings())
        sel.Selections = self.Selections
        sel.Caller = "ANALYSIS::SELECTIONS"
        if not sel.MakeSelections(self): return

        self.DumpSelections()
        self.DumpTracer(self.SampleName)
        self.FlushEvents(get_ev)

    def __Graph__(self):
        if self.Graph is None: return
        get = sum(self._get["graph"].values(), [])
        get_ev = sum(self._get["event"].values(), [])
        c = cCheckDifference(get_ev, get, self.Threads)

        if len(c): self.RestoreEvents(c)
        if len(get) and self.DataCache: self.RestoreGraphs(get)
        elif not len(get): pass
        elif len(get_ev): pass
        else: return

        if self.Tree: pass
        elif not len(self.ShowTrees): return
        elif len(self.ShowTrees) > 1: return
        else: self.Tree = self.ShowTrees[0]

        self.GetGraph = True
        if self.GraphName: pass
        elif len(self.ShowGraphs) == 0: pass
        elif len(self.ShowGraphs) > 1: return
        else: self.GraphName = self.Graph.__name__

        cur = self.ShowLength
        try: gr_l = cur[self.Tree + "/" + self.GraphName]
        except KeyError: gr_l = 0
        try: ev_l = cur[self.Tree + "/" + self.EventName]
        except KeyError: ev_l = 0

        content = self[self.GraphName]
        if not content: pass
        elif (gr_l == ev_l) and gr_l: return

        gr = GraphGenerator()
        gr.Caller = "ANALYSIS::GRAPH"
        gr.ImportSettings(self.ExportSettings())
        try: x = self.ShowLength[self.Tree + "/" + self.GraphName]
        except KeyError: x = 0

        if gr.EventStop is None: pass
        elif self.EventStop > x: gr.EventStop = self.EventStop - x
        elif self.EventStop <= x: return
        else: pass

        if not len(c) and len(get_ev) and content: return
        if not gr.MakeGraphs(self): return
        if not self.DataCache: return
        self.DumpGraphs()
        self.DumpTracer(self.SampleName)
        return True


    def __Event__(self):
        if self.Event is None: return
        get = sum(self._get["event"].values(), [])
        if len(get) and self.EventCache: self.RestoreEvents(get)
        elif not len(get): pass

        if self.Tree: pass
        elif len(self.ShowTrees) == 0: pass
        elif len(self.ShowTrees) > 1: return
        else: self.Tree = self.ShowTrees[0]

        if self.EventName: pass
        elif len(self.ShowEvents) > 1: return
        else: self.EventName = self.ShowEvents[0]
        self.GetEvent = True

        self.Files = None
        self.Files = self._get["get"]
        if not len(self.Files): return

        ev = EventGenerator()
        ev.Caller = "ANALYSIS::EVENT"
        ev.ImportSettings(self.ExportSettings())
        ev.EventStop = self.EventStop
        try: x = self.ShowLength[self.Tree + "/" + self.EventName]
        except KeyError: x = 0

        if ev.EventStop is None: pass
        elif self.EventStop > x: ev.EventStop = self.EventStop - x
        elif self.EventStop <= x: return
        else: pass

        if ev.MakeEvents(self.SampleName, self): pass
        else: return

        if not self.EventCache: return
        self.DumpEvents()
        self.DumpTracer(self.SampleName)
        return True

    def __Optimizer__(self):
        if self.Model is None: return
        op = Optimizer()
        op.Start(self)

    def __LoadSample__(self):
        tracer = self._CheckForTracer()
        l = len(self.SampleMap)
        if not l: self.SampleMap = ""
        for name in self.SampleMap:
            self.SampleName = name
            if not len(name): name = None
            if not tracer: pass
            else: self.RestoreTracer(tracer, name)
            search(self)
            self.__Event__()
            self.__Selection__()
            self.__FeatureAnalysis__()
            self.__Graph__()
        return True

    def Launch(self):
        self.__build__()
        self.__LoadSample__()
        self.__RandomSampler__()
        self.__Optimizer__()
        self.WhiteSpace()
        return True

    def preiteration(self) -> bool:
        if self.triggered: pass
        else: self.Launch()

        if len(self.ShowSelections): self.GetSelection = True
        if len(self.ShowEvents): self.GetEvent = True
        if len(self.ShowGraphs): self.GetGraph = True

        if self.Tree: pass
        elif not len(self.ShowTrees): return True
        else: self.Tree = self.ShowTrees[0]
        return False
