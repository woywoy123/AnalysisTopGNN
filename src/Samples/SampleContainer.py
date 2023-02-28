from AnalysisTopGNN.Notification import SampleContainer
from .ROOTFile import ROOTFile
import copy 

class SampleContainer:

    def __init__(self):
        self.ROOTFiles = {}
        self._Hashes = {}
        self._EventMap = {}
        self._locked = False
    
    def AddEvent(self, Name, Event):
        if Name not in self.ROOTFiles:
            self.ROOTFiles[Name] = ROOTFile(Name)
        self.ROOTFiles[Name].AddEvent(Event) 
    
    def HashToROOT(self, _hash):
        for name in self.ROOTFiles:
            if _hash in self.ROOTFiles[name]:
                return name

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
        return list(self._Hashes.values())

    def ClearEvents(self):
        tmp = copy.deepcopy(self)
        for name in tmp.ROOTFiles:
            tmp.ROOTFiles[name].ClearEvents()
        tmp.list(True)
        tmp.hash(True)
        tmp._locked = True
        return tmp

    def RestoreEvents(self, events):
        if isinstance(events, list):
            events = {i.Filename : i for i in events}
        rest = {}
        for i in events:
            name = self.HashToROOT(i)
            if name not in rest:
                rest[name] = []
            rest[name].append(events[i])
        
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
        if key in self._Hashes and isinstance(key, str):
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
    
    def __add__(self, other):
        names = list(self.ROOTFiles) + list(other.ROOTFiles)
        samples = list(self.ROOTFiles.values()) + list(other.ROOTFiles.values())
        
        self.ROOTFiles = {}
        for name, sample in zip(names, samples):
            if name not in self.ROOTFiles:
                self.ROOTFiles[name] = sample
                continue
            self.ROOTFiles[name] += sample
        self.hash()
        self.list()
        return self
   
    def __contains__(self, key):
        if key in self._Hashes:
            return True
        if key in self._EventMap:
            return True
        if key in self.ROOTFiles:
            return True 
        return False

