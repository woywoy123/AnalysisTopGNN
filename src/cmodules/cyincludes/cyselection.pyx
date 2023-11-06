# distutils: language = c++
# cython: language_level = 3

from cyselection cimport CySelectionTemplate
from cytypes cimport event_t, selection_t
from cytypes cimport code_t

from AnalysisG._cmodules.ParticleTemplate import ParticleTemplate
from AnalysisG.Tools.General import Tools
from AnalysisG.Tools import Code

from cython.operator cimport dereference
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map, pair
from libcpp cimport bool

import pickle

try: import pyc
except ModuleNotFoundError: print("ERROR: pyc not installed..")

cdef string enc(str val): return val.encode("UTF-8")
cdef str env(string val): return val.decode("UTF-8")

cdef string consolidate(map[string, string]* inpt, string* src):
    cdef pair[string, string] itr
    t = Tools()
    trg = None
    if src.size(): trg = pickle.loads(dereference(src))
    for itr in dereference(inpt):
        if trg is None: trg = pickle.loads(itr.second)
        else: trg = t.MergeData(trg, pickle.loads(itr.second))
    inpt.clear()
    src.clear()
    return b"" if trg is None else pickle.dumps(trg)


class Neutrino(ParticleTemplate):
    def __init__(self):
        self.Type = "nu"
        ParticleTemplate.__init__(self)
        self.chi2 = None


cdef class SelectionTemplate:

    cdef CySelectionTemplate* ptr
    cdef selection_t* sel
    cdef _params_
    cdef code_t _code

    def __cinit__(self):
        self.ptr = new CySelectionTemplate()
        self.sel = &(self.ptr.selection)
        cdef string name = enc(self.__class__.__name__)
        self.ptr.set_event_name(self.sel, name)
        if not self.sel._params_.size(): self._params_ = None
        else: self._params_ = pickle.loads(self.sel._params_)

    def __init__(self): pass
    def __dealloc__(self): del self.ptr
    def __name__(self) -> str: return env(self.sel.event_name)
    def __hash__(self) -> int: return int(self.hash[:8], 0)

    def __eq__(self, other) -> bool:
        if not self.is_self(other): return False
        cdef SelectionTemplate o = other
        return self.ptr[0] == o.ptr[0]

    def __radd__(self, other):
        if other == 0: return self
        else: return self.__add__(other)

    def __add__(self, SelectionTemplate other):
        self.ptr.iadd(other.ptr)
        cdef string* data = &self.sel.pickled_data
        cdef map[string, string]* data_m = &self.sel.data_merge
        self.sel.pickled_data = consolidate(data_m, data)

        cdef string* stra = &self.sel.pickled_strategy_data
        cdef map[string, string]* stra_m = &self.sel.strat_merge
        self.sel.pickled_strategy_data = consolidate(stra_m, stra)

        self.__setstate__(dereference(self.sel))
        return self

    def __getstate__(self) -> selection_t:
        cdef str key
        cdef dict pkl = {}
        for key in list(self.__dict__):
            if key.startswith("_"): continue
            pkl[key] = self.__dict__[key]
        self.ptr.selection.pickled_data = pickle.dumps(pkl)
        return self.ptr.Export()

    def __setstate__(self, selection_t inpt):
        self.ptr.Import(inpt)
        if not inpt.pickled_data.size(): return
        cdef str key
        cdef dict pkls = pickle.loads(inpt.pickled_data)
        for key in pkls: setattr(self, key, pkls[key])

    def __scrapecode__(self):
        co = Code(self)
        cdef code_t code = co.__getstate__()
        self.sel.code_hash = code.hash
        self._code = code
        return code

    cpdef Px(self, float val, float phi):
        return pyc.Transform.Px(val, phi)

    cpdef Py(self, float val, float phi):
        return pyc.Transform.Py(val, phi)

    cpdef MakeNu(self, s_, chi2 = None, gev = False):
        if s_ == 0.0: return None
        if not len(s_): return None

        # Convert back to MeV if set to gev, because the input 
        # leptons and b-quark are in MeV
        scale = 1000 if gev else 1
        nu = Neutrino()
        nu.px = s_[0] * scale
        nu.py = s_[1] * scale
        nu.pz = s_[2] * scale
        nu.e = (nu.px**2 + nu.py**2 + nu.pz**2) ** 0.5
        if chi2 is not None: nu.chi2 = chi2
        return nu

    cpdef NuNu(
        self, q1, q2, l1, l2, ev,
        float mT=172.5 * 1000, float mW=80.379 * 1000, float mN=0, float zero=1e-12,
        bool gev = False
    ):
        scale = 1/1000 if gev else 1
        inpt = []
        inpt.append([[q1.pt*scale, q1.eta, q1.phi, q1.e*scale]])
        inpt.append([[q2.pt*scale, q2.eta, q2.phi, q2.e*scale]])
        inpt.append([[l1.pt*scale, l1.eta, l1.phi, l1.e*scale]])
        inpt.append([[l2.pt*scale, l2.eta, l2.phi, l2.e*scale]])

        inpt.append([[ev.met*scale, ev.met_phi]])
        inpt.append([[mW*scale, mT*scale, mN*scale]])
        inpt.append(zero)

        sol = pyc.NuSol.Polar.NuNu(*inpt)
        if sol[2] is None: return []

        _s1, _s2, diag, n_, h_per1, h_per2, nsols = sol
        _s1, _s2, diag = _s1.tolist(), _s2.tolist(), diag.tolist()

        o = {}
        for k, j, c in zip(_s1[0], _s2[0], diag[0]):
            o[c] = [self.MakeNu(k, c, gev), self.MakeNu(j, c, gev)]
        return [o[s] for s in sorted(o)]

    cpdef Nu(
        self, q1, l1, ev,
        S=[100, 0, 0, 100],
        mT=172.5*1000, mW=80.379*1000, mN=0, zero=1e-12,
        gev = False
    ):
        scale = 1/1000 if gev else 1

        inpt = []
        inpt.append([[q1.pt*scale, q1.eta, q1.phi, q1.e*scale]])
        inpt.append([[l1.pt*scale, l1.eta, l1.phi, l1.e*scale]])

        inpt.append([[ev.met*scale, ev.met_phi]])
        inpt.append([[mW*scale, mT*scale, mN*scale]])

        inpt.append([[S[0], S[1]], [S[2], S[3]]])
        inpt.append(zero)
        sol, chi2 = pyc.NuSol.Polar.Nu(*inpt)
        sol, chi2 = sol.tolist(), chi2.tolist()
        nus = {c2 : self.MakeNu(s, c2, gev) for s, c2 in zip(sol[0], chi2[0])}
        return [nus[s] for s in sorted(nus)]

    def is_self(self, inpt) -> bool:
        if isinstance(inpt, SelectionTemplate): return True
        return issubclass(inpt.__class__, SelectionTemplate)

    def clone(self) -> SelectionTemplate:
        return self.__class__()

    def Selection(self, event):
        return True

    def Strategy(self, event):
        return True

    def __select__(self, event):
        res = self.Selection(event)
        if res is None: res = ""
        if isinstance(res, str): return self.ptr.CheckSelection(enc(res))
        if type(res).__name__ == "bool": return self.ptr.CheckSelection(<bool>res)
        return True

    def __strategy__(self, event):
        self.ptr.StartTime()
        res = self.Strategy(event)
        self.ptr.EndTime()

        if res is None: res = ""
        if isinstance(res, str): return self.ptr.CheckStrategy(enc(str(res)))
        if type(res).__name__ == "bool": return self.ptr.CheckStrategy(<bool>res)
        self.sel.pickled_strategy_data = pickle.dumps(res)
        return True

    def __processing__(self, event):
        cdef event_t ev
        ev.event_index   = event.index
        ev.event_hash    = enc(event.hash)
        ev.event_tagging = enc(event.Tag)
        ev.event_tree    = enc(event.Tree)
        ev.event_root    = enc(event.ROOT)
        ev.weight        = event.weight
        self.ptr.RegisterEvent(&ev)
        if self.__params__ is None: pass
        else: self.sel._params_ = pickle.dumps(self.__params__)

        if not self.sel.allow_failure:
            if self.__select__(event): pass
            else: return False

            if self.__strategy__(event): return True
            else: return False

        try:
            if self.__select__(event): pass
            else: return False
        except Exception as inst:
            self.sel.errors[enc(str(inst))] += 1
            return self.ptr.CheckSelection(enc(str(inst)+"::Error"))

        try: return self.__strategy__(event)
        except Exception as inst:
            self.sel.errors[enc(str(inst))] += 1
            return self.ptr.CheckStrategy(enc(str(inst)+"::Error"))


    @property
    def __params__(self):
        if not self.sel._params_.size(): return self._params_
        return pickle.loads(self.sel._params_)

    @__params__.setter
    def __params__(self, val):
        self._params_ = val
        self.sel._params_ = pickle.dumps(val)

    @property
    def CutFlow(self) -> dict:
        cdef pair[string, int] it
        cdef dict output = {}
        for it in self.sel.cutflow: output[env(it.first)] = it.second
        return output

    @property
    def AverageTime(self): return self.ptr.Mean()

    @property
    def StdevTime(self): return self.ptr.StandardDeviation()

    @property
    def Luminosity(self): return self.ptr.Luminosity()

    @property
    def nPassedEvents(self): return self.sel.selection_weights.size()

    @property
    def TotalEvents(self): return self.sel.all_weights.size()

    @property
    def AllWeights(self): return self.sel.all_weights

    @property
    def SelectionWeights(self): return self.sel.selection_weights

    @property
    def AllowFailure(self): return self.sel.allow_failure

    @AllowFailure.setter
    def AllowFailure(self, bool val): self.sel.allow_failure = val

    @property
    def hash(self) -> str: return env(self.ptr.Hash())

    @property
    def code_hash(self) -> str: return env(self.sel.code_hash)

    @property
    def index(self) -> int: return self.sel.event_index

    @property
    def Tag(self) -> str: return env(self.sel.event_tagging)

    @Tag.setter
    def Tag(self, str val): self.sel.event_tagging = enc(val)

    @property
    def Tree(self) -> str: return env(self.sel.event_tree)

    @property
    def cached(self) -> bool: return self.sel.cached

    @cached.setter
    def cached(self, bool val) -> bool: self.sel.cached = val

    @property
    def ROOT(self) -> str: return env(self.sel.event_root)

    @property
    def selection(self) -> bool: return self.ptr.is_selection

    @property
    def SelectionName(self) -> str: return env(self.sel.event_name)

    @property
    def Residual(self):
        if not self.sel.pickled_strategy_data.size(): return None
        return pickle.loads(self.sel.pickled_strategy_data)

    @property
    def code(self): return self._code

    @code.setter
    def code(self, code_t val): self._code = val


