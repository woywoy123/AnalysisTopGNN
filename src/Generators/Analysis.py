from AnalysisG.IO import PickleObject, UnpickleObject
from .SelectionGenerator import SelectionGenerator
from AnalysisG.Templates import FeatureAnalysis
from AnalysisG.Notification import _Analysis
from .SampleGenerator import RandomSamplers
from .EventGenerator import EventGenerator
from .GraphGenerator import GraphGenerator
from AnalysisG.Tracer import SampleTracer
from AnalysisG.Settings import Settings
from .Interfaces import _Interface
from .Optimizer import Optimizer
from typing import Union


class Analysis(_Analysis, Settings, SampleTracer, _Interface):
    def __init__(
        self,
        SampleDirectory: Union[str, dict, list, None] = None,
        Name: Union[str] = None,
    ):
        self.Caller = "ANALYSIS"
        _Analysis.__init__(self)
        _Interface.__init__(self)
        Settings.__init__(self)
        SampleTracer.__init__(self)
        if Name is None and SampleDirectory is None:
            return
        self.InputSample(Name, SampleDirectory)

    def __build__(self):
        if self._cPWD is not None: return
        if not self._condor: self.StartingAnalysis()
        self._cPWD = self.pwd()

        if self.OutputDirectory is None:
            self.OutputDirectory = self.pwd()
        else:
            self.OutputDirectory = self.abs(self.OutputDirectory)
        self.OutputDirectory = (
            self.AddTrailing(self.OutputDirectory, "/") + self.ProjectName
        )
        if self.PurgeCache: self._WarningPurge()
        if not self._condor: self._BuildingCache()

    def __Event__(self):
        process = {}
        for i in list(self.Files):
            f = [j for j in self.Files[i] if i + "/" + j not in self]
            if len(f) != 0: process[i] = f
        if len(process) == 0: return True
        if self.Event == None: return False
        if self.EventStop != None and len(self) >= self.EventStop:
            return True

        self.Files = process
        ev = EventGenerator()
        ev.ImportSettings(self)
        ev.Caller = "ANALYSIS::EVENT"
        if not ev.MakeEvents(): return False

        ev.EventCache = self.EventCache
        if self.EventCache: ev.DumpEvents()
        self += ev
        return True

    def __Graph__(self):
        if self.EventGraph == None: return True

        process = {}
        if self.EventCacheLen != self.DataCacheLen:
            process.update(self.Files)
        if len(process) == 0 and len(self.Files) != 0:
            return True
        self.RestoreEvents()
        failed = False
        if self.TestFeatures: failed = self.__FeatureAnalysis__()
        if failed: return False

        gr = GraphGenerator(self)
        gr.ImportSettings(self)
        gr.Caller = "ANALYSIS::GRAPH"
        if not gr.MakeGraphs(): return False

        gr.DataCache = self.DataCache
        if self.DataCache: gr.DumpEvents()
        self += gr
        return True

    def __FeatureAnalysis__(self):
        if self.EventGraph is None: return True
        if not self.TestFeatures: return
        tests = [i for i, _ in zip(self.GetEventCacheHashes(), range(self.nEvents))]
        self.ForceTheseHashes(tests)
        f = FeatureAnalysis()
        f.ImportSettings(self)
        return f.TestEvent([i for i in self], self.EventGraph)

    def __Selection__(self):
        if len(self.Selections) == 0 and len(self.Merge) == 0:
            return
        if self.EventCacheLen == 0: return
        self.EventCache = True
        self.RestoreEvents()

        pth = self.OutputDirectory + "/Selections/"
        sel = SelectionGenerator(self)
        sel.Threads = self.Threads # Fix after merge
        sel.ImportSettings(self)
        sel.Caller = "ANALYSIS::SELECTIONS"
        sel.MakeSelection()
        del sel

    def __RandomSampler__(self):
        pth = self.OutputDirectory + "/Training/DataSets/"
        if not self.TrainingSize: return
        if self.TrainingName + ".pkl" in self.ls(pth): return
        if not self.kFolds: self.kFolds = 1

        output = {}
        r = RandomSamplers()
        r.Caller = self.Caller
        if self.TrainingSize:
            output = r.MakeTrainingSample(self.todict(), self.TrainingSize)
        if self.kFolds:
            output.update(
                r.MakekFolds(
                    self.todict(), self.kFolds, self.BatchSize, self.Shuffle, True
                )
            )
        if len(output) == 0: return
        self.mkdir(pth)
        PickleObject(output, pth + self.TrainingName)

    def __Optimizer__(self):
        if self.Model == None and self.Optimizer == None:
            return
        op = Optimizer(self)
        op.Launch()

    def __CollectCode__(self):
        code = {}
        if self.Event is not None:
            ev = EventGenerator()
            ev.ImportSettings(self)
            code.update(ev.MakeEvents())

        if self.EventGraph is not None:
            gr = GraphGenerator()
            gr.ImportSettings(self)
            code.update(gr.MakeGraphs())

        if len(self.Selections) != 0:
            sel = SelectionGenerator(self)
            sel.ImportSettings(self)
            for name in self.Selections:
                sel.AddSelection(name, self.Selections[name])
            code.update(sel.MakeSelection())
        if self.Model is not None:
            code["Model"] = Optimizer(self).GetCode()
        return code

    def Launch(self):
        if self._condor: return self.__CollectCode__()
        if not self.__LoadSample__(): return False
        self.__build__()
        self.__Selection__()
        self.__RandomSampler__()
        self.__Optimizer__()
        self.WhiteSpace()
        return True

    def __LoadSample__(self):
        self.__build__()
        tracer = self._CheckForTracer()
        for i in self.SampleMap:
            self.Files = self.SampleMap[i]
            self.SampleName = i
            if tracer: self.RestoreTracer()
            if not self.__Event__(): return False
            if not self.__Graph__(): return False
        if self.len == 0: self.RestoreTracer()
        if len(self) == 0: return False
        return True

    def __preiteration__(self):
        if self.len == 0:
            if self._cPWD is not None and self.len != 0:
                return False
            ok = self.__LoadSample__()
            return not ok
        if self.EventCache: self.RestoreEvents()
        if self.DataCache: self.RestoreEvents()
        return self.EmptySampleList()
