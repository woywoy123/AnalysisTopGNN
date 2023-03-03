from .Hashing import Hashing 
from AnalysisTopGNN.Vectors import IsIn

class ROOTFile(Hashing):
    
    def __init__(self, Filename, Threads = 1, chnk = 1):
        self.HashMap = {}
        self.Filename = Filename
        self.EventMap = {}
        self._lock = False
        self._len = -1
        self._Threads = Threads
        self._chnk = chnk
    
    def MakeHash(self):
        for i in self.EventMap:
            _hash = self.MD5(self.Filename + "/" + str(self.EventMap[i].EventIndex))
            self.EventMap[i].Filename = _hash
            self.HashMap[_hash] = self.EventMap[i]

    def AddEvent(self, Event):
        self.EventMap[Event.EventIndex] = Event
        self._len += 1
    
    def __len__(self):
        return self._len

    def list(self):
        return list(self.EventMap.values())
    
    def hash(self):
        if len(self) != len(self.HashMap) and self._lock == False:
            self.MakeHash()
        return list(self.HashMap)
    
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
        self.HashMap = {h : False for h in set(hashes)}
        for _hash, evnt in zip(hashes, evnts):
            if self.HashMap[_hash] == False: 
                self.HashMap[_hash] = evnt
                continue
                
            if isinstance(evnt, str):
                continue
            self.HashMap[_hash] = evnt

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
