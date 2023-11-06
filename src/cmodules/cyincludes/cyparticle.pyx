# distuils: language = c++
# cython: language_level = 3
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map, pair
from libcpp cimport bool

from cyparticle cimport CyParticleTemplate
from cytypes cimport particle_t

from typing import Union
import pickle

cdef string enc(str val): return val.encode("UTF-8")
cdef str env(string val): return val.decode("UTF-8")

cdef class ParticleTemplate:

    cdef CyParticleTemplate* ptr
    cdef list Children
    cdef list Parent
    cdef bool _pkld
    cdef particle_t state

    def __cinit__(self):
        self.ptr = new CyParticleTemplate()
        self.state = self.ptr.state
        self.Children = []
        self.Parent = []
        self._pkld = False

    def __init__(self): pass
    def __dealloc__(self): del self.ptr
    def __hash__(self): return int(self.hash[:8], 0)

    def __add__(self, ParticleTemplate other) -> ParticleTemplate:
        cdef ParticleTemplate _p = self.clone()
        _p.ptr.iadd(other.ptr)
        _p.ptr.iadd(self.ptr)
        _p.Children = list(set(other.Children + self.Children))
        _p.Parent = list(set(other.Parent + self.Parent))
        return _p

    def __radd__(self, other) -> ParticleTemplate:
        if not self.is_self(other): return self
        return self.__add__(other)

    def __iadd__(self, ParticleTemplate other) -> ParticleTemplate:
        self.Children = list(set(other.Children + self.Children))
        self.Parent   = list(set(other.Parent + self.Parent))
        self.ptr.iadd(other.ptr)
        return self

    def __getstate__(self) -> tuple:
        if self._pkld: return ({}, self.state)
        self._pkld = True
        self.state = self.ptr.Export()

        cdef str key
        cdef list get = list(self.__dict__)
        cdef dict pkl = { key : self.__dict__[key] for key in get}
        pkl["Children"] = self.Children
        pkl["Parent"] = self.Parent
        return (pkl, self.state)

    def __setstate__(self, tuple inpt):
        cdef str key
        self.ptr.Import(inpt[1])
        for key in inpt[0]: setattr(self, key, inpt[0][key])

    def __eq__(self, other) -> bool:
        if not self.is_self(other): return False
        cdef ParticleTemplate o = other
        return self.ptr[0] == o.ptr[0]

    def __getleaves__(self):
        cdef str i
        cdef pair[string, string] x
        cdef dict leaves = {}
        for x in self.ptr.leaves: leaves[env(x.first)] = env(x.second)
        for i, v in zip(self.__dict__, self.__dict__.values()):
            if not isinstance(v, str): continue
            leaves[i] = v
        return leaves


    def __build__(self, dict variables):
        cdef ParticleTemplate p
        cdef dict inpt = {}
        cdef dict x = {}
        cdef bool get
        cdef str k
        cdef dict lv, p_

        cdef list keys = list(self.__getleaves__())
        for k in variables:
            if k.split("/")[-1] not in keys: continue
            try: inpt[k] = variables[k].tolist()
            except AttributeError:
                if isinstance(variables[k], str): continue
                inpt[k] = variables[k]

        if not len(inpt): return {}
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
            if not get: self.__build__(x)
            else:
                p = self.clone()
                p_ = {k.split("/")[-1] : x[k] for k in x}
                for k in p_:
                    try: setattr(p, k, p_[k])
                    except KeyError: pass
                self.Children.append(p)
        return {i : obj for i, obj in enumerate(self.Children)}

    def clone(self) -> ParticleTemplate:
        v = self.__class__
        v = v()
        v.Type = self.Type
        return v

    def is_self(self, inpt) -> bool:
        if isinstance(inpt, ParticleTemplate): return True
        return issubclass(inpt.__class__, ParticleTemplate)

    def DeltaR(self, ParticleTemplate other) -> float:
        return self.ptr.DeltaR(other.ptr)

    @property
    def hash(self) -> str: return env(self.ptr.hash())

    @property
    def index(self) -> int: return self.ptr.state.index

    @property
    def px(self) -> double: return self.ptr.px()

    @property
    def py(self) -> double: return self.ptr.py()

    @property
    def pz(self) -> double: return self.ptr.pz()

    @property
    def pt(self) -> double: return self.ptr.pt()

    @property
    def eta(self) -> double: return self.ptr.eta()

    @property
    def phi(self) -> double: return self.ptr.phi()

    @property
    def e(self) -> double: return self.ptr.e()

    @property
    def Mass(self) -> double: return self.ptr.mass()

    @property
    def charge(self) -> double: return self.ptr.charge()

    @property
    def pdgid(self) -> int: return self.ptr.pdgid()

    @property
    def symbol(self) -> str : return env(self.ptr.symbol())

    @property
    def Type(self) -> str: return env(self.ptr.state.type)

    @property
    def lepdef(self) -> vector[int]: return self.ptr.state.lepdef

    @property
    def nudef(self) -> vector[int]: return self.ptr.state.nudef

    @property
    def is_lep(self) -> bool: return self.ptr.is_lep()

    @property
    def is_nu(self) -> bool: return self.ptr.is_nu()

    @property
    def is_b(self) -> bool: return self.ptr.is_b()

    @property
    def is_add(self) -> bool: return self.ptr.is_add()

    @property
    def LeptonicDecay(self) -> bool:
        cdef vector[particle_t] ch
        cdef ParticleTemplate x
        for x in self.Children: ch.push_back(x.__getstate__()[1])
        return self.ptr.lep_decay(ch)

    @index.setter
    def index(self, val: Union[str, int, float, list]):
        try: self.ptr.state.index = val
        except TypeError:
            try: self.ptr.addleaf(b'index', enc(val))
            except: self.__dict__["index"] = val

    @px.setter
    def px(self, val: Union[str, double]):
        try: self.ptr.px(val)
        except TypeError: self.ptr.addleaf(b'px', enc(val))

    @py.setter
    def py(self, val: Union[str, double]):
        try: self.ptr.py(val)
        except TypeError: self.ptr.addleaf(b'py', enc(val))

    @pz.setter
    def pz(self, val: Union[str, double]):
        try: self.ptr.pz(val)
        except TypeError: self.ptr.addleaf(b'pz', enc(val))

    @pt.setter
    def pt(self, val: Union[str, double]):
        try: self.ptr.pt(val)
        except TypeError: self.ptr.addleaf(b'pt', enc(val))

    @eta.setter
    def eta(self, val: Union[str, double]):
        try: self.ptr.eta(val)
        except TypeError: self.ptr.addleaf(b'eta', enc(val))

    @phi.setter
    def phi(self, val: Union[str, double]):
        try: self.ptr.phi(val)
        except TypeError: self.ptr.addleaf(b'phi', enc(val))

    @e.setter
    def e(self, val: Union[str, double]):
        try: self.ptr.e(val)
        except TypeError: self.ptr.addleaf(b'e', enc(val))

    @Mass.setter
    def Mass(self, val: Union[str, double]):
        try: self.ptr.mass(val)
        except TypeError: self.ptr.addleaf(b'Mass', enc(val))

    @charge.setter
    def charge(self, val: Union[str, double]):
        try: self.ptr.charge(val)
        except TypeError: self.ptr.addleaf(b'charge', enc(val))

    @pdgid.setter
    def pdgid(self, val: Union[str, double, int]):
        try: self.ptr.pdgid(val)
        except TypeError: self.ptr.addleaf(b'pdgid', enc(val))

    @symbol.setter
    def symbol(self, str val):
        self.ptr.symbol(enc(val))

    @Type.setter
    def Type(self, str val):
        self.ptr.state.type = enc(val)

    @lepdef.setter
    def lepdef(self, vector[int] val):
        self.ptr.state.lepdef = val

    @nudef.setter
    def nudef(self, vector[int] val):
        self.ptr.state.nudef = val

    @property
    def Children(self) -> list:
        self.Children = list(set(self.Children))
        return self.Children

    @Children.setter
    def Children(self, inpt):
        if isinstance(inpt, list): self.Children += inpt
        else: self.Children += [inpt]

    @property
    def Parent(self) -> list:
        self.Parent = list(set(self.Parent))
        return self.Parent

    @Parent.setter
    def Parent(self, inpt):
        if isinstance(inpt, list): self.Parent += inpt
        else: self.Parent += [inpt]




