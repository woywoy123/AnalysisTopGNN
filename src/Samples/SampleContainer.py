from AnalysisTopGNN.Notification import SampleContainer
from AnalysisTopGNN.Tools import Threading
from .ROOTFile import ROOTFile
import copy 

class SampleContainer:

    def __init__(self):
        self.ROOTFiles = {}
        self._Hashes = {}
        self._EventMap = {}
        self._locked = False
        self.Threads = 1
        self.chnk = 1
    
    def AddEvent(self, Name, Event):
        if Name not in self.ROOTFiles:
            self.ROOTFiles[Name] = ROOTFile(Name, self.Threads, self.chnk)
        self.ROOTFiles[Name].AddEvent(Event) 
    
    def HashToROOT(self, _hash):
        for name in self.ROOTFiles:
            if _hash in self.ROOTFiles[name]:
                return name
        return False 

    def list(self, force = False):
        if len(self._EventMap) != len(self) or force:
            lst = [ev for name in self.ROOTFiles for ev in self.ROOTFiles[name].list()]
            self._EventMap = {i : ev for i, ev in zip(range(len(lst)), lst)}
        return list(self._EventMap.values())
    
    def dict(self):
        self.hash(True)
        return self._Hashes

    def hash(self, force = False):
        if len(self._Hashes) != len(self) or force:
            self._Hashes = {_hash : self.ROOTFiles[name][_hash] for name in self.ROOTFiles for _hash in self.ROOTFiles[name].hash()}
            self.list(True)
        return list(self._Hashes.keys())

    def ClearEvents(self):
        tmp = copy.deepcopy(self)
        for name in tmp.ROOTFiles:
            tmp.ROOTFiles[name].ClearEvents()
        tmp.list(True)
        tmp.hash(True)
        tmp._locked = True
        return tmp

    def RestoreEvents(self, events, threads = 12, chnk = 100):
        def function(inpt):
            out = []
            for ev in inpt:
                name = self.HashToROOT(ev.Filename)
                if name == False:
                    out.append([ev, False])
                else:
                    out.append([ev.Filename, ev, name])
            return out
        if isinstance(events, dict):
            events = list(events.values())
        
        th = Threading(events, function, threads, chnk)
        th.VerboseLevel = 0
        th.Title = "RESTORE"
        th.Start()
        events = {i[0] : i[1] for i in th._lists if i[1]}
        rest = {i[2] : [] for i in th._lists if i[1]}
        for k in th._lists:
            if not k[1]:
                continue
            rest[k[2]].append(k[1])
        for name in rest:
            self.ROOTFiles[name].RestoreEvents(rest[name])
        self.list(True)
        self.hash(True)
        self._locked = False

    def __len__(self):
        return sum([len(self.ROOTFiles[name]) for name in self.ROOTFiles])  

    def __getitem__(self, key):
        self.hash()
        self.list()
        if isinstance(key, str) == False:
            return False
        v = self.ROOTFiles.get(key)
        if key in self.ROOTFiles:
            return self.ROOTFiles[key]
        if key in self._Hashes:
            return self._Hashes[key]
        if key in self._EventMap:
            return self._EventMap[key]
        return False
    
    def __setitem__(self, key, obj):
        self.hash()
        self.list()
        for name in self.ROOTFiles:
            if key not in self.ROOTFiles[name]:
                continue
            self.ROOTFiles[name][key] += obj
            break
    def __radd__(self, other):
        smpl = SampleContainer()
        if other == 0:
            smpl += self
            return smpl
        smpl += self
        smpl += other
        return smpl

    def __add__(self, other):
        smpl = SampleContainer()

        names = list(self.ROOTFiles) + list(other.ROOTFiles)
        samples = list(self.ROOTFiles.values()) + list(other.ROOTFiles.values())
        
        smpl.ROOTFiles = {}
        for name, sample in zip(names, samples):
            if name not in smpl.ROOTFiles:
                smpl.ROOTFiles[name] = sample
                continue
            if smpl.ROOTFiles[name]._lock:
                smpl.ROOTFiles[name] = sample
                continue
            smpl.ROOTFiles[name] += sample
        smpl.hash()
        smpl.list()
        return smpl
   
    def __contains__(self, key):
        
        if key in self.ROOTFiles:
            return True
        if self.__len__() != len(self._Hashes):
            self.hash(True)
        if key in self._Hashes:
            return True
        if key in self._EventMap:
            return True

        return False

