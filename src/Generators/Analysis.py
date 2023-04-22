from .SelectionGenerator import SelectionGenerator 
from AnalysisG.Notification import _Analysis
from .EventGenerator import EventGenerator 
from .GraphGenerator import GraphGenerator 
from AnalysisG.Tracer import SampleTracer
from AnalysisG.Settings import Settings
from .Interfaces import _Interface

class Analysis(_Analysis, Settings, SampleTracer, _Interface):
    
    def __init__(self):
        self.Caller = "ANALYSIS"
        _Analysis.__init__(self)
        _Interface.__init__(self)
        Settings.__init__(self)
        SampleTracer.__init__(self)
  
    @property
    def __build__(self):
        
        if self._cPWD is not None: return 
        self.StartingAnalysis
        self._cPWD = self.pwd
        if self.OutputDirectory is None: self.OutputDirectory = self.pwd
        else: self.OutputDirectory = self.abs(self.OutputDirectory)
        
        self.OutputDirectory = self.AddTrailing(self.OutputDirectory, "/") + self.ProjectName
        if self.PurgeCache: self._WarningPurge
        self._BuildingCache 

    @property
    def __Selection__(self):
        sel = SelectionGenerator(self)
        sel.ImportSettings(self)
        for name in self.Selections: sel.AddSelection(name, self.Selections[name])
        sel.MakeSelection
    
    @property 
    def __Event__(self):
        process = {}
        for i in list(self.Files): 
            f = [j for j in self.Files[i] if i + "/" + j not in self]
            if len(f) != 0: process[i] = f
        if len(process) == 0: return True 
        if self.Event == None: return False  
        self.Files = process 
        ev = EventGenerator()
        ev.ImportSettings(self)
        if not ev.MakeEvents: return False
        self += ev
        if self.EventCache: self.DumpEvents
        return True 

    @property
    def __Graph__(self):
        if self.EventGraph == None: return True
        process = {}
        for i in list(self.Files): 
            f = {j : len([l for l in self[i + "/" + j] if l.Event]) for j in self.Files[i]}
            f = [j for j in f if j != 0] 
            if len(f) != 0: process[i] = f
        if len(process) == 0 and len(self.Files) != 0: return True 

        self.Files = process 
        gr = GraphGenerator(self)
        gr.ImportSettings(self)
        if not gr.MakeGraphs: return False
        self += gr
        if self.DataCache: self.DumpEvents
        return True 

    def __preiteration__(self):
        if len(self) == 0: self.Launch
        return self.EmptySampleList

    @property
    def Launch(self):
        self.__build__
        tracer = self._CheckForTracer
        for i in self.SampleMap:
            self.Files = self.SampleMap[i]
            self.SampleName = i
            if tracer: self.RestoreEvents
            if not self.__Event__: return False
            if not self.__Graph__: return False
        if len(self.Selections) != 0: self.__Selection__
        self.WhiteSpace()

