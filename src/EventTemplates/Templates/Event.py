from AnalysisTopGNN.Tools import VariableManager
import copy 

class EventTemplate(VariableManager):
    def __init__(self):
        VariableManager.__init__(self)
        self.Type = "Event"
        self.Trees = []
        self.Branches = []
        self.Leaves = []
        self._Store = None
        self.iter = -1

    def GetKey(self, obj, Excld = []):
        return {j : i for i, j in zip(obj.__dict__.keys(), obj.__dict__.values()) if i not in Excld and isinstance(j, str)}

    def DefineObjects(self):
        for name in self.Objects:
            self.Leaves += list(self.GetKey(self.Objects[name], ["Index", "Type"]))
        self.Leaves += list(self.GetKey(self, ["Type", "Objects", "iter"]))

    def _Compile(self, ClearVal):
        def Recursive(lst, name):
            for i in lst:
                if len(lst[i]) == 0:
                    continue

                p = getattr(self, name)
                if len(p) == len(lst[i]):
                   for k in p:
                        setattr(p[k], i, lst[i][k])
                else:
                    tmp = [l for f in lst[i] for l in f]
                    indx = [f for f in range(len(lst[i])) for k in lst[i][f]]
                    for k in p:
                        setattr(p[k], i, tmp[k])
                        p[k].Index = indx[k]

        for name, obj in zip(self.Objects, self.Objects.values()):
            maps = self.GetKey(obj, ["Type"])
            tmp = { maps[i] : self._Store[i] for i in self._Store if i in maps }

            n_prt = []
            for k, p in zip(tmp.values(), tmp.keys()):
                try:
                    le = [t for j in k for t in j]
                except:
                    le = [j for j in k]
                n_prt.append(len(le))

            n_prt = min(list(set(n_prt)))
            x = {k : copy.deepcopy(obj) for k in range(n_prt)}
            for t in x:
                setattr(x[t], "Index", t)
            setattr(self, name, x)
            Recursive(tmp, name)
        
        maps = self.GetKey(self)
        tmp = { maps[i] : self._Store[i] for i in self._Store if i in maps }
        for i in tmp:
            try:
                tmp[i] = float(tmp[i])
            except:
                tmp[i] = float(tmp[i][0])
            setattr(self, i, tmp[i])
        self.CompileEvent() 

        if ClearVal:
            del self._Store
            names = [i for i in self.Objects]
            del self.Objects
            del self.Leaves
            del self.Branches
            del self.Trees
            
            for i in names:
                for l in self.DictToList(getattr(self, i)):
                    maps = self.GetKey(l, ["Index", "Type"])
                    if len(maps) == 0: 
                        continue
                    for t in maps.values():
                        self.Warning("POTENTIAL MEMORY LEAK IN EVENT PARTICLE: " + i + " -> " + t + ":::" + maps[t])
    
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
    
    def CompileParticles(self, ClearVal = False):
        for i in self.Objects.values():
            l = getattr(self, i)
            l = CompileParticles(l, self.Objects[i]).Compile(ClearVal)
            self.SetAttribute(i, l)
 
