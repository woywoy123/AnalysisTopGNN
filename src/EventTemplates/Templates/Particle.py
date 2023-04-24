from .Manager import VariableManager
from AnalysisTopGNN.Vectors import *
from AnalysisTopGNN.Samples.Hashing import Hashing 
from base64 import b64encode, b64decode

class ParticleTemplate(VariableManager):
    def __init__(self):
        self.index = -1
        VariableManager.__init__(self)
        self.Parent = []
        self.Children = []
        for p in ['phi', 'eta', 'pt', 'e', 'px', 'py', 'pz']:
            self.__dict__['_' + p] = None

    @property
    def px(self):
        self._px = Px(self._pt, self._phi) if self._pt != None and self._phi != None else self._px
        return self._px

    @property
    def py(self):
        self._py = Py(self._pt, self._phi) if self._pt != None and self._phi != None else self._py
        return self._py

    @property
    def pz(self):
        self._pz = Pz(self._pt, self._eta) if self._pt != None and self._eta != None else self._pz
        return self._pz

    @property
    def eta(self):
        self._eta = Eta(self._px, self._py, self._pz) if self._px != None and self._py != None and self._pz != None else self._eta
        return self._eta

    @property
    def phi(self):
        self._phi = Phi(self._px, self._py) if self._px != None and self._py != None else self._phi
        return self._phi

    @property
    def pt(self):
        self._pt = PT(self._px, self._py) if self._px != None and self._py != None else self._pt
        return self._pt

    @property
    def e(self):
        if IsIn(["_e"], self.__dict__) and self._e != None:
            return self._e
        m = self.m if IsIn(["m"], self.__dict__) else 0
        self._e = energy(m, self.px, self.py, self.pz)
        return self._e

    @phi.setter
    def phi(self, value):
        self._phi = value

    @eta.setter
    def eta(self, value):
        self._eta = value

    @pt.setter
    def pt(self, value):
        self._pt = value

    @e.setter
    def e(self, value):
        self._e = value

    @px.setter
    def px(self, value):
        self._px = value

    @py.setter
    def py(self, value):
        self._py = value

    @pz.setter
    def pz(self, value):
        self._pz = value

    def DeltaR(self, P):
        return deltaR(P.eta, self.eta, P.phi, self.phi)

    @property
    def Mass(self):
        return PxPyPzEMass(self.px, self.py, self.pz, self.e)

    def _istype(self, lst):
        if IsIn(["pdgid"], self.__dict__):
            return abs(self.pdgid) in lst
        return False

    @property
    def is_lep(self):
        return self._istype([11, 13, 15])

    @property
    def is_nu(self):
        return self._istype([12, 14, 16])

    @property
    def is_b(self):
        return self._istype([5])

    @property
    def is_add(self):
        return not (self.is_lep or self.is_nu or self.is_b)

    @property
    def LeptonicDecay(self):
        return sum([1 for k in self.Children if abs(k.pdgid) in [11, 12, 13, 14, 15, 16]]) > 0

    @property
    def Symbol(self):
        PDGID = {
                  1 : "d"           ,  2 : "u"             ,  3 : "s",
                  4 : "c"           ,  5 : "b"             ,  6 : "t",
                 11 : "e"           , 12 : "$\\nu_e$"      , 13 : "$\mu$",
                 14 : "$\\nu_{\mu}$", 15 : "$\\tau$"       , 16 : "$\\nu_{\\tau}$",
                 21 : "g"           , 22 : "$\\gamma$"}
        
        try:
            return PDGID[abs(self.pdgid)] 
        except:
            return ""

    @property
    def _Hash(self):
        self._hash = "" if not IsIn(["_hash"], self.__dict__) else self._hash
        if self._hash == "":
            x = Hashing()
            self._hash = x.MD5(str({i : self.__dict__[i] for i in self.__dict__ if i not in ["Children", "Parent", "Symbol", "Mass"]}))
            self._hash = b64encode(self._hash.encode("utf-8"))
            self._hash = int.from_bytes(b64decode(self._hash[:8]), "big")
        return self._hash

    def __del__(self):
        for i in self.__dict__:
            val = self.__dict__[i]
            del val, i

    def __radd__(self, other):
        if other == 0:
            p = ParticleTemplate()
            p.px = self.px
            p.py = self.py
            p.pz = self.pz
            p.e = self.e
            return p
        else:
            return self.__add__(other)

    def __add__(self, other):
        particle = ParticleTemplate()
        particle.px = self.px + other.px
        particle.py = self.py + other.py
        particle.pz = self.pz + other.pz
        particle.e = self.e + other.e

        particle.Children += self.Children
        particle.Children += [p for p in other.Children if p not in particle.Children]

        return particle

    def __eq__(self, other):
        if other == None:
            return False
        return self._Hash == other._Hash
    
    def __hash__(self):
        return int(self._Hash)

    def __str__(self, caller = False):
        string = ""
        if "pdgid" in self.__dict__:
            string += "========\n"
            string += "pdgid: " + str(self.pdgid) + " "
            string += "Symbol: " + self.Symbol + " " 
        string += "eta: " + str(self.eta) + "\n"
        string += "phi: " + str(self.phi) + "\n"
        string += "pt: " + str(self.pt) + "\n"
        string += "\n========\n"
        
        if caller:
            return string

        for i in self.Children:
            string += " -> " + i.__str__(caller = True)
        return string
