from .Hashing import Hashing 
from AnalysisTopGNN.Vectors import IsIn
from AnalysisTopGNN.Tools import Threading


class ROOTFile(Hashing):
    
    def __init__(self, Filename, Threads = 1, chnk = 1):
        self.HashMap = {}
        self.Filename = Filename
        self.EventMap = {}
        self.EventCompiled = {}
        self._lock = False
        self._len = 0
        self._lenC = 0
        self.Threads = Threads
        self.chnk = chnk
        self._iter = None
    
    def MakeHash(self):
        for i in self.EventMap.values():
            self.HashMap[i.Filename] = i
        self._len = len(self.HashMap)

    def AddEvent(self, Event):
        self.EventMap[Event.EventIndex] = Event
        self._len += 1
    
    def __len__(self):
        return self._len

    def list(self):
        _o = list(self.EventMap)
        _o.sort()
        return [ self.EventMap[i] for i in _o ]
    
    def Compiled(self):
        if len(self.EventCompiled) != self._lenC or self._lenC == 0:
            self.EventCompiled = {i : self.EventMap[i] for i in self.EventMap if self.EventMap[i].Compiled}
        self._lenC = len(self.EventCompiled)
        return self._lenC 

    def hash(self):
        if len(self) != len(self.HashMap) and self._lock == False:
            self.MakeHash()
        return list(self.HashMap)

    def __iter__(self):
        self._iter = iter(self.HashMap.values())
        return self
    
    def __next__(self):
        return next(self._iter)

    def __getitem__(self, key):
        if IsIn([key], self.HashMap):
            return self.HashMap[key]
        if IsIn([key], self.EventMap):
            return self.EventMap[key]
        return False
    
    def __setitem__(self, key, obj):
        if IsIn([key], self.HashMap) and self._lock == False:
            self.EventMap[self.HashMap[key].EventIndex] 
            return self
        if IsIn([key], self.EventMap) and self._lock == False:
            self.HashMap[self.EventMap[key].Filename] = obj
            self.EventMap[key] = obj
            return self
         
    def __contains__(self, key):
        if IsIn([str(key)], self.HashMap):
            return True 
        if IsIn([str(key)], self.EventMap):
            return True
        return False

    def __add__(self, other):
        hashes = self.hash() + other.hash() 
        evnts = list(self.HashMap.values()) + list(other.HashMap.values())
        self.HashMap = {h : False for h in hashes}
        for _hash, evnt in zip(hashes, evnts):
            if isinstance(evnt, str):
                continue

            self.EventMap[evnt.EventIndex] = evnt
            if self.HashMap[_hash] == False: 
                self.HashMap[_hash] = evnt
            
            self.HashMap[_hash] = evnt if isinstance(self.HashMap[_hash], str) else self.HashMap[_hash]
            if evnt.Compiled and self.HashMap[_hash].Compiled == False:
                self.HashMap[_hash] = evnt
                self.EventCompiled[_hash] = evnt

        self.EventMap = self.EventMap if self._lock else {i : "" if isinstance(ev, str) else ev.UpdateIndex(i) for i, ev in zip(range(len(self.HashMap)), self.HashMap.values())}
        self._len = len(self.EventMap)
        return self
    
    def ClearEvents(self):
        if self._lock:
            return self
        self._lock = True
        self.HashMap = {i.Filename : "" for i in self.HashMap.values()}
        self.EventMap = {i.EventIndex : "" for i in self.EventMap.values()}

    def RestoreEvents(self, events):
        if isinstance(events, dict):
            events = list(events.values())
        self.HashMap |= { i.Filename : i for i in events if IsIn([i.Filename], self.HashMap) }
        self.EventMap |= { i.EventIndex : i for i in events if i.EventIndex in self.EventMap }
        self._lock = False
