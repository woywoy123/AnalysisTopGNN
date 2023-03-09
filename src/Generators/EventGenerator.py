from AnalysisTopGNN.IO import File
from AnalysisTopGNN.Samples.Event import EventContainer
from AnalysisTopGNN.Samples.Managers import SampleTracer

from AnalysisTopGNN.Notification import EventGenerator_
from AnalysisTopGNN.Tools import Threading, Tools
from .Settings import Settings, _Code

def _MakeEvents(inpt, _prgbar):
     
    lock, bar = _prgbar
    _e = inpt[0][2]
    r = inpt[0][0]
    inpt = [i[1] for i in inpt] 
    
    All = [b.split("/")[-1] for b in r.Branches] + [l.split("/")[-1] for l in r.Leaves]
    __iter = {Tree : r._Reader[Tree].iterate(All, library = "np", step_size = len(inpt), entry_start = min(inpt), entry_stop = max(inpt)+1 ) for Tree in r.Trees}
    __iter = {Tree : next(__iter[Tree]) for Tree in __iter}
    root = r.ROOTFile
    
    it = 0
    out = []
    for i in inpt:
        o = EventContainer()
        o.EventIndex = i
        for tr in r.Trees: 
            o.Trees[tr] = _Code().CopyInstance(_e)
            o.Trees[tr]._Store = {k : __iter[tr][k][it].tolist() for k in __iter[tr]} 
            o.Trees[tr].Tree = tr
            o.Trees[tr]._SampleIndex = i
            o.Filename = root
        o.MakeEvent(True)
        with lock:
            bar.update(1)
        out.append([root, o])
        it += 1

    __iter = None 
    return out

class EventGenerator(EventGenerator_, Settings, Tools, SampleTracer):
    def __init__(self, InputDir = False, EventStart = -1, EventStop = None):

        self.Caller = "EVENTGENERATOR"
        Settings.__init__(self)
        SampleTracer.__init__(self)

        if isinstance(InputDir, dict):
            self.InputDirectory |= InputDir
        else:
            self.InputDirectory = InputDir
        self.EventStart = EventStart
        self.EventStop = EventStop

    def SpawnEvents(self):
        
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
                cmp.append([F_i, indx, obj]) 
            
            th = Threading(cmp, _MakeEvents, self.Threads, self.chnk)
            th.VerboseLevel = self.VerboseLevel
            th.Title = "READING/COMPILING EVENT"
            cmp = None
            th.Start()
            for i in th._lists:
                self.AddROOTFile(i[0], i[1])
            del th
        self.CheckSpawnedEvents()

