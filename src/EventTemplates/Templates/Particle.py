from .Manager import VariableManager
from AnalysisTopGNN.Vectors import * 

class ParticleTemplate(VariableManager):
    def __init__(self):
        self.index = -1
        VariableManager.__init__(self)
        self.Parent = []
        self.Children = []

    def DeltaR(self, P):
        return deltaR(P.eta, self.eta, P.phi, self.phi)
    
    @property
    def Mass(self):
        return PxPyPzEMass(self._px, self._py, self._pz, self._e)

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
    def _px(self):
        self.px = Px(self.pt, self.phi) if IsIn(["pt", "phi"], self.__dict__) else self.px
        return self.px

    @property
    def _py(self):
        self.py = Py(self.pt, self.phi) if IsIn(["pt", "phi"], self.__dict__) else self.py
        return self.py

    @property
    def _pz(self):
        self.pz = Pz(self.pt, self.eta) if IsIn(["pt", "eta"], self.__dict__) else self.pz
        return self.pz

    @property
    def _eta(self):
        self.eta = Eta(self.px, self.py, self.pz) if IsIn(["px", "py", "pz"], self.__dict__) else self.eta
        return self.eta
    
    @property
    def _phi(self):
        self.phi = Phi(self.px, self.py) if IsIn(["px", "py"], self.__dict__) else self.phi   
        return self.phi

    @property
    def _pt(self):
        self.pt = PT(self.px, self.py) if IsIn(["px", "py"], self.__dict__) else self.pt   
        return self.pt
    
    @property 
    def _e(self):
        if IsIn(["e"], self.__dict__):
            return self.e
        m = self.m if IsIn(["m"], self.__dict__) else 0
        self.e = energy(m, self._px, self._py, self._pz)
        return self.e
    
    @property
    def LeptonicDecay(self):
        return sum([1 for k in self.Children if abs(k.pdgid) in [11, 12, 13, 14, 15, 16]]) > 0

    def __del__(self):
        for i in self.__dict__:
            val = self.__dict__[i]
            del val, i

    def __radd__(self, other):
        if other == 0:
            p = ParticleTemplate()
            p.__dict__["px"] = self._px
            p.__dict__["py"] = self._py
            p.__dict__["pz"] = self._pz
            p.__dict__["e"] = self._e
            p._eta, p._pt, p._phi, p._e 
            return p
        else:
            return self.__add__(other)

    def __add__(self, other):
        particle = ParticleTemplate()
        particle.__dict__["px"] = self._px + other._px
        particle.__dict__["py"] = self._py + other._py
        particle.__dict__["pz"] = self._pz + other._pz 
        particle.__dict__["e"] = self._e + other._e 

        particle._eta, particle._pt, particle._phi, particle._e 

        particle.Children += self.Children
        particle.Children += [p for p in other.Children if p not in particle.Children]

        return particle
    
    def __str__(self, caller = False):
        PDGID = {
                  1 : "d"           ,  2 : "u"             ,  3 : "s",
                  4 : "c"           ,  5 : "b"             ,  6 : "t",
                 11 : "e"           , 12 : "$\\nu_e$"      , 13 : "$\mu$",
                 14 : "$\\nu_{\mu}$", 15 : "$\\tau$"       , 16 : "$\\nu_{\\tau}$",
                 21 : "g"           , 22 : "$\\gamma$"}

        string = ""
        if "pdgid" in self.__dict__:
            string += "======== "
            string += "pdgid: " + str(self.pdgid) + " "
            string += "Symbol: " + PDGID[abs(self.pdgid)] + " ====\n"
        string += "eta: " + str(self.eta) + "\n"
        string += "phi: " + str(self.phi) + "\n"
        string += "pt: " + str(self.pt) + "\n"

        if caller:
            return string

        for i in self.Children:
            string += " -> " + i.__str__(caller = True)
        return string

