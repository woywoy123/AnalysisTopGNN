from time import time 
from AnalysisTopGNN.Templates import ParticleTemplate
from AnalysisTopGNN.Generators import Settings
from AnalysisTopGNN.Tools import Tools
from AnalysisTopGNN.IO import PickleObject
from PyC.NuSol.Tensors import NuDoublePtEtaPhiE, NuNuDoublePtEtaPhiE

class Neutrino(ParticleTemplate):
    
    def __init__(self):
        self.Type = "nu"
        ParticleTemplate.__init__(self)
        self.px = None 
        self.py = None 
        self.pz = None

class Selection(Settings, Tools):
    def __init__(self):
        self.Caller = "SELECTION"
        Settings.__init__(self)
    
    @property
    def _t1(self):
        self.__t1 = time()
    
    @property 
    def _t2(self):
        self._TimeStats.append(time() - self.__t1)

    def Selection(self, event):
        return True

    def Strategy(self, event):
        pass

    def MakeNu(self, s_):
        if sum(s_) == 0.:
            return None
        nu = Neutrino()
        nu.px = s_[0]*1000
        nu.py = s_[1]*1000
        nu.pz = s_[2]*1000
        return nu

    def NuNu(self, q1, q2, l1, l2, ev, mT = 172.5, mW = 80.379, mN = 0, zero = 1e-12):
        sol = NuNuDoublePtEtaPhiE(
                q1.pt/1000., q1.eta, q1.phi, q1.e/1000., 
                q2.pt/1000., q2.eta, q2.phi, q2.e/1000., 
                l1.pt/1000., l1.eta, l1.phi, l1.e/1000., 
                l2.pt/1000., l2.eta, l2.phi, l2.e/1000., 
                ev.met/1000., ev.met_phi, 
                mT, mW, mN, zero)
       
        skip = sol[0].tolist()[0]
        _s1 = sol[1].tolist()[0]
        _s2 = sol[2].tolist()[0]
        if skip:
            return []
        o = [ [self.MakeNu(k), self.MakeNu(j)] for k, j in zip(_s1, _s2) ]
        return [p for p in o if p[0] != None and p[1] != None]
   
    def Nu(self, q1, l1, ev, S = [100, 0, 0, 100], mT = 172.5, mW = 80.379, mN = 0, zero = 1e-12):
        sol = NuDoublePtEtaPhiE(         
                q1.pt/1000., q1.eta, q1.phi, q1.e/1000., 
                l1.pt/1000., l1.eta, l1.phi, l1.e/1000., 
                ev.met/1000., ev.met_phi, 
                S[0], S[1], S[2], S[3], mT, mW, mN, zero)
        skip = sol[0].tolist()[0]
        if skip:
            return []
        _s1 = sol[1].tolist()[0]
        return [self.MakeNu(_s1)]

    def Sort(self, inpt, descending = False):
        if isinstance(inpt, list):
            inpt.sort()
            return inpt
        _tmp = list(inpt)
        _tmp.sort()
        if descending:
            _tmp.reverse()
        inpt = {k : inpt[k] for k in _tmp}
        return inpt
    
    def _EventPreprocessing(self, event):
        if self.Tree == None:
            self.Tree = list(event.Trees)[0]
        
        if self._hash == None:
            self._hash = event.Filename
        
        if self.Selection(event.Trees[self.Tree]) == False:
            return  
        self._t1
        o = self.Strategy(event.Trees[self.Tree])
        self._t2
        if isinstance(o, str) and "->" in o:
            if o not in self._CutFlow:
                self._CutFlow[o] = 0
            self._CutFlow[o] += 1
        else:
            self._Residual += [o] if o != None else []
        if self._OutDir:
            o = self._OutDir
            PickleObject(self.__dict__, self._OutDir + "/" + self._hash)
            self.__init__()
            self._OutDir = o
        del event
            
    def __call__(self, Ana = None):
        if Ana == None:
            return self
        for i in Ana:
            self._EventPreprocessing(i)
   
    def __eq__(self, other):
        if other == None:
            return False
        t1 = self.GetSourceCode(self)
        t2 = other.GetSourceCode(other)
        return t1 == t2
    
    def __radd__(self, other):
        if other == 0:
            return self
        return self.__add__(other)
    
    def __add__(self, other):
        if isinstance(other, list):
            out = []
            for i in other:
                out += [self.__add__(i)[-1]]
            out.append(self)
            return out
        if self != other:
            return [self, other]
        
        self._Code = []
        out = self.CopyInstance(self)
        out.__init__()
        keys = set(list(out.__dict__) + list(other.__dict__))
        for i in keys:
            if i == "_hash":
                out._hash = [self._hash] if isinstance(self._hash, str) else self._hash
                out._hash += [other._hash] if isinstance(other._hash, str) else other._hash
                continue
            if i in ["Trees", "_OutDir", "Tree", "Type", "Caller"]:
                out.__dict__[i] = self.__dict__[i]
                continue 
            if i == "_CutFlow":
                k_ = set(list(self.__dict__[i]) + list(other.__dict__[i]))
                self.__dict__[i] |= {l : 0 for l in k_ if l not in self.__dict__[i]}
                other.__dict__[i] |= {l : 0 for l in k_ if l not in other.__dict__[i]}
            if i not in self.__dict__:
                self.__dict__[i] == other.__dict__[i]
                continue
            out.__dict__[i] = self.MergeData(self.__dict__[i], other.__dict__[i])
        return out
    
    def RestoreSettings(self, inpt):
        for i in inpt:
            self.__dict__[i] = inpt[i]
        return self
            
