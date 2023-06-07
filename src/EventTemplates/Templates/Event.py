from .Manager import VariableManager
import copy 
import sys
sys.setrecursionlimit(100000000)

class EventTemplate(VariableManager):
    def __init__(self):
        VariableManager.__init__(self)
        self.Type = "Event"
        self.Trees = []
        self.Branches = []
        self.Leaves = []
        self._Store = None
        self._SampleIndex = -1
        self.Lumi = 1
        self._Deprecated = False
        self._CommitHash = False
        self.eventNumber = "eventNumber"

    def DefineObjects(self):
        for name in self.Objects:
            self.Leaves += list(self.GetKey(self.Objects[name], ["Index", "Type"]))
        self.Leaves += list(self.GetKey(self, ["Type", "Objects", "iter"]))
    
    def __NestedListToList(self, lst):
        if isinstance(lst, list):
            return lst
        elif isinstance(lst, dict): 
            out = []
            for i in lst.values():
                out += self.__NestedListToList(i)
            return out
        return [lst]

    def GetKey(self, obj, Excld = []):
        return {j : i for i, j in zip(obj.__dict__.keys(), obj.__dict__.values()) if i not in Excld and isinstance(j, str)}

    def _Compile(self, ClearVal = True):
        def MakeParticle(obj, partDic, name):
            _objm = self.GetKey(obj)
            for j in _objm:
                if j not in partDic:
                    continue
                obj.__dict__[_objm[j]] = partDic[j]
            if name not in self.__dict__:
                self.__dict__[name] = []
            self.__dict__[name].append(obj)

        def RecursivePopulate(store, name):
            partDic = {}
            try:
                tmp = {key : store[key][0].tolist() for key in store if len(store[key]) > 0}
                partDic |= {key : store[key].pop().tolist() for key in tmp}
            except AttributeError:
                partDic |= {key : store[key].pop() for key in store if len(store[key]) > 0}
           
            if len(partDic) == 0:
                return None
            
            leng = {}
            for j in partDic:
                if isinstance(partDic[j], list) == False:
                    continue
                if len(partDic[j]) == 0:
                    continue
                l = len(partDic[j])
                if l not in leng:
                    leng[l] = []
                leng[l].append({j : partDic[j]})
            
            if len(leng) == 0:
                if len(self.__NestedListToList(partDic)) != 0:
                    MakeParticle(copy.deepcopy(self.Objects[name]), partDic, name)
            else:
                key = max(list(leng))
                if len(leng[key]) < 4:
                    MakeParticle(copy.deepcopy(self.Objects[name]), partDic, name)
                else:
                    RecursivePopulate(partDic, name)

            return RecursivePopulate(store, name)
        
        maps = self.GetKey(self)
        tmp = { i : self._Store[i] for i in maps if i in self._Store }
        for i in tmp:
            self.__dict__[maps[i]] = tmp[i]
            del self._Store[i]
      
        objmap = {i : self.GetKey(self.Objects[i]) for i in self.Objects}
        self._Store = {i : {k : self.__NestedListToList(self._Store[k]) for k in objmap[i] if k in self._Store} for i in objmap }
        
        for i in self._Store:
            RecursivePopulate(self._Store[i], i)
        
        for i in self.Objects:
            if i in self.__dict__:
                self.__dict__[i] = {k : obj for k, obj in zip(range(len(self.__dict__[i])), self.__dict__[i])}
            else:
                self.__dict__[i] = {}

        self.CompileEvent()

        if ClearVal:
            del self._Store
            del self.Objects
            del self.Leaves
            del self.Branches
            del self.Trees
            
    def CompileEvent(self):
        pass

    def DictToList(self, inp): 
        out = []
        for i in inp:
            if isinstance(inp, list):
                out += [i]
            elif isinstance(inp, dict):
                out.append(inp[i])
            else:
                out.append(i)
        return out
