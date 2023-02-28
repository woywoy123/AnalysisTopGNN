from AnalysisTopGNN.IO import File
from AnalysisTopGNN.Samples.Event import EventContainer
from AnalysisTopGNN.Samples.Managers import SampleTracer

from AnalysisTopGNN.Notification import EventGenerator_
from AnalysisTopGNN.Tools import Threading, Tools
from .Settings import Settings

class EventGenerator(EventGenerator_, Settings, Tools, SampleTracer):
    def __init__(self, InputDir = False, EventStart = 0, EventStop = None):

        self.Caller = "EVENTGENERATOR"
        Settings.__init__(self)
        SampleTracer.__init__(self)

        if isinstance(InputDir, dict):
            self.InputDirectory |= InputDir
        else:
            self.InputDirectory = InputDir

    def SpawnEvents(self):
        def PopulateEvent(eventDict, indx, F):
            EC = EventContainer()
            for tr in eventDict: 
                EC.Trees[tr] = self.CopyInstance(self.Event)
                EC.Trees[tr]._Store = eventDict[tr]
                EC.Trees[tr].Tree = tr
                EC.Trees[tr]._SampleIndex = indx
                EC.Filename = F
            EC.EventIndex = indx
            return EC

        def function(inpt, _prgbar):
            
            out = []
            lock, bar = _prgbar
            r = inpt[0][0]
            c = [i[1] for i in inpt]
            All = [b.split("/")[-1] for b in r.Branches] + [l.split("/")[-1] for l in r.Leaves]
            __iter = {Tree : r._Reader[Tree].iterate(All, library = "np", step_size = 1, entry_start = min(c), entry_stop = max(c)+1 ) for Tree in r.Trees}
            for i in c:
                _iter = {Tree : next(__iter[Tree]) for Tree in __iter}
                out.append(PopulateEvent(_iter, i, r.ROOTFile))
                if self.Caller == "ANALYSIS":
                    out[-1].MakeEvent(True)
                with lock:
                    bar.update(1)
            return out
                 
        self.CheckSettings()
        self.CheckEventImplementation()

        self.AddCode(self.Event)
        obj = self.CopyInstance(self.Event)
        self.CheckVariableNames(obj)
        for p in obj.Objects:
            self.AddCode(obj.Objects[p])
        
        if self._dump:
            return self

        self.Files = self.ListFilesInDir(self.InputDirectory, extension = ".root")
        self.CheckROOTFiles()  
        
        it = -1
        for F in self.DictToList(self.Files):
            F_i = File(F)
            F_i.Trees += obj.Trees
            F_i.Branches += obj.Branches
            F_i.Leaves += obj.Leaves 
            F_i.ValidateKeys()
            cmp = []
            for indx in range(len(F_i)):
                it += 1
                if self.EventStart > it and self.EventStart != -1:
                    continue
                if self.EventStop != None and self.EventStop < it:
                    break
                cmp.append([F_i, indx]) 

            th = Threading(cmp, function, self.Threads, self.chnk)
            th.VerboseLevel = self.VerboseLevel
            th.Title = "READING/COMPILING EVENT"
            th.Start()
            for i in th._lists:
                self.AddROOTFile(F, i)
        self.CheckSpawnedEvents()

    def CompileEvent(self, ClearVal = True):
        
        def function(inp, _prgbar):
            out = []
            for k in inp:
                k.MakeEvent(ClearVal)
                out.append(k)
            return out
        if self._dump:
            return self
        TH = Threading(self.SampleContainer.list(), function, self.Threads,  self.chnk)
        TH.VerboseLevel = self.VerboseLevel
        TH.Start()
        for ev in TH._lists:
            self.SampleContainer[ev.Filename] = ev
