#distutils: language = c++
#cython: language_level = 3

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool
from typing import Union
from Templates cimport CyParticleTemplate

cdef class ParticleTemplate(object):
    cdef CyParticleTemplate* ptr
    cdef public list Children
    cdef public list Parent
    cdef dict _leaves
    cdef bool _state

    def __cinit__(self):
        self.ptr = new CyParticleTemplate()
        self._leaves = {}
        self._state = False

    def __init__(self):
        self.Children = []
        self.Parent = []

    def __dealloc__(self):
        del self.ptr

    def __add__(ParticleTemplate self, ParticleTemplate other) -> ParticleTemplate:
        cdef ParticleTemplate _p = self.clone()
        _p.ptr[0] += self.ptr[0]
        _p.ptr[0] += other.ptr[0]
        return _p

    def __radd__(ParticleTemplate self, other) -> ParticleTemplate:
        if not issubclass(other.__class__, ParticleTemplate):
            return self.__add__(self.clone())
        return self.__add__(other)

    def __eq__(self, other) -> bool:
        if not issubclass(other.__class__, ParticleTemplate): return False
        cdef ParticleTemplate s = self
        cdef ParticleTemplate o = other
        s.ptr.Hash()
        o.ptr.Hash()
        return s.ptr[0] == o.ptr[0]

    def __hash__(self) -> int:
        return int(self.hash[:8], 0)

    def __str__(self) -> str:
        cdef str i = "============\n"
        if self.pdgid != 0:
            i += " pdgid: " + str(self.pdgid) + "\n"
            i += "Symbol: " + str(self.symbol) + "\n"
        i += "    pt: " + str(self.pt) + "\n"
        i += "   eta: " + str(self.eta) + "\n"
        i += "   phi: " + str(self.phi) + "\n"
        i += "energy: " + str(self.e) + "\n"
        return i

    def __getstate__(self):
        state = {}
        state_keys = list(self.__interpret__)
        state_keys += list(self.__dict__)
        state_keys += [i for i in self.__dir__() if not i.startswith("_")]
        for i in set(state_keys):
            if i == "clone": continue
            try: v = getattr(self, i)
            except: continue
            if type(v).__name__ == "builtin_function_or_method": continue
            state.update({i : v})
        return state

    def __setstate__(self, inpt):
        for i in inpt:
            try: setattr(self, i, inpt[i])
            except: pass

    @property
    def __interpret__(self):
        cdef str i
        if self._init: return self._leaves
        for i, v in zip(self.__dict__, self.__dict__.values()):
            if isinstance(v, list): continue
            if isinstance(v, dict): continue
            self._leaves[i] = v
        return self._leaves

    @__interpret__.setter
    def __interpret__(self, dict inpt):
        cdef str k
        cdef dict x
        cdef bool get

        try:
            inpt = {k.split("/")[-1] : inpt[k] for k in inpt}
            inpt = {k : inpt[self._leaves[k]] for k in self._leaves}
        except KeyError: pass

        while True:
            x = {}
            get = False
            for k in list(inpt):
                try: inpt[k] = inpt[k].tolist()
                except AttributeError: pass

                try: x[k] = inpt[k].pop()
                except AttributeError: x[k] = inpt[k]
                except IndexError: pass

                if k not in x: continue

                try: x[k] = x[k].item()
                except AttributeError: pass

                try: len(x[k])
                except TypeError: get = True

            if len(x) == 0: break
            if not get: self.__interpret__ = x
            else:
                p = self.clone()
                p.__setstate__(x)
                p._init = True
                self.Children.append(p)

    def clone(self):
        v = self.__new__(self.__class__)
        v.__init__()
        v.Type = self.Type
        v.__interpret__
        return v

    @property
    def Type(self) -> str:
        return self.ptr.Type.decode("UTF-8")

    @Type.setter
    def Type(self, str val):
        self.ptr.Type = val.encode("UTF-8")

    @property
    def index(self) -> int:
        return self.ptr.index

    @index.setter
    def index(self, val: Union[int, float, str]): 
        if isinstance(val, int): self.ptr.index = val
        elif isinstance(val, float): self.ptr.index = <int>val
        elif isinstance(val, str): self._leaves["index"] = val

    @property
    def hash(self) -> str:
        return self.ptr.Hash().decode("UTF-8")

    @property
    def px(self) -> double:
        return self.ptr.px()

    @px.setter
    def px(self, val: Union[str, float]):
        if isinstance(val, float): self.ptr.px(<double>val)
        elif isinstance(val, str): self._leaves["px"] = val

    @property
    def py(self) -> double:
        return self.ptr.py()

    @py.setter
    def py(self, val: Union[str, float]):
        if isinstance(val, float): self.ptr.py(<double>val)
        elif isinstance(val, str): self._leaves["py"] = val

    @property
    def pz(self) -> double:
        return self.ptr.pz()

    @pz.setter
    def pz(self, val: Union[str, float]):
        if isinstance(val, float): self.ptr.pz(<double> val)
        elif isinstance(val, str): self._leaves["pz"] = val

    @property
    def pt(self) -> double:
        return self.ptr.pt()

    @pt.setter
    def pt(self, val: Union[str, float]):
        if isinstance(val, float): self.ptr.pt(<double> val)
        elif isinstance(val, str): self._leaves["pt"] = val

    @property
    def eta(self) -> double:
        return self.ptr.eta()

    @eta.setter
    def eta(self, val: Union[str, float]):
        if isinstance(val, float): self.ptr.eta(<double> val)
        elif isinstance(val, str): self._leaves["eta"] = val

    @property
    def phi(self) -> double:
        return self.ptr.phi()

    @phi.setter
    def phi(self, val: Union[str, float]):
        if isinstance(val, float): self.ptr.phi(<double> val)
        elif isinstance(val, str): self._leaves["phi"] = val

    @property
    def e(self) -> double:
        return self.ptr.e()

    @e.setter
    def e(self, val: Union[str, float]):
        if isinstance(val, float): self.ptr.e(<double>val)
        elif isinstance(val, str): self._leaves["e"] = val

    @property
    def Mass(self) -> double:
        return self.ptr.Mass()

    @Mass.setter
    def Mass(self, val: Union[str, float]):
        if isinstance(val, float): self.ptr.Mass(<double>val)
        elif isinstance(val, str): self._leaves["Mass"] = val

    def DeltaR(self, ParticleTemplate other) -> float:
        return self.ptr.DeltaR(other.ptr[0])

    @property
    def pdgid(self) -> int:
        return self.ptr.pdgid()

    @pdgid.setter
    def pdgid(self, val: Union[str, float, int]):
        if isinstance(val, int): self.ptr.pdgid(<int>val)
        elif isinstance(val, float): self.ptr.pdgid(<int>val)
        elif isinstance(val, str): self._leaves["pdgid"] = val

    @property
    def charge(self) -> float:
        return self.ptr.charge()

    @charge.setter
    def charge(self, val: Union[str, float, int]):
        if isinstance(val, float): self.ptr.charge(<double>val)
        elif isinstance(val, int): self.ptr.charge(<double>val)
        elif isinstance(val, str): self._leaves["charge"] = val

    @property
    def symbol(self) -> str:
        return self.ptr.symbol().decode("UTF-8")

    @symbol.setter
    def symbol(self, string value):
        self.ptr.symbol(value.decode("UTF-8"))

    @property
    def is_lep(self) -> bool:
        return self.ptr.is_lep()

    @property
    def is_nu(self) -> bool:
        return self.ptr.is_nu()

    @property
    def is_b(self) -> bool:
        return self.ptr.is_b()

    @property
    def is_add(self) -> bool:
        return not (self.is_lep or self.is_nu or self.is_b)

    @property
    def lepdef(self) -> vector[int]:
        return self.ptr._lepdef

    @property
    def nudef(self) -> vector[int]:
        return self.ptr._nudef

    @lepdef.setter
    def lepdef(self, vector[signed int] val):
        self.ptr._lepdef = val

    @nudef.setter
    def nudef(self, vector[signed int] val):
        self.ptr._nudef = val

    @property
    def _init(self) -> bool:
        return self._state

    @_init.setter
    def _init(self, bool val): 
        self._state = val

    @property
    def LeptonicDecay(self):
        return len([i for i in self.Children if i.is_nu]) != 0


