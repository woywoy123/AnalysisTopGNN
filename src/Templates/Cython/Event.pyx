#distutils: language = c++
#cython: language_level = 3

from Templates cimport CyEventTemplate
from libcpp.string cimport string
from libcpp.map cimport map
from libcpp cimport bool
from typing import Union

cdef class EventTemplate:
    cdef CyEventTemplate* ptr
    cdef dict _leaves
    cdef list _Trees
    cdef list _Branches
    cdef list _Leaves
    cdef dict _Objects
    cdef str _name

    def __cinit__(self):
        self.ptr = new CyEventTemplate()
        self._Trees = []
        self._Branches = []
        self._Leaves = []
        self._Objects = {}
        self._leaves = {"event" : {}}

    def __init__(self):
        self._name = self.__class__.__name__

    def __name__(self) -> str:
        return self._name

    def __dealloc__(self): del self.ptr

    def __hash__(self) -> int: return int(self.hash[:8], 0)

    def __eq__(self, other) -> bool:
        if not issubclass(other.__class__, EventTemplate): return False
        if self.__name__() != other.__name__(): return False
        return self.hash == other.hash

    def __getstate__(self) -> dict:
        cdef dict state = {}
        cdef list state_keys = []
        cdef str i
        state_keys += list(self.__interpret__)
        state_keys += list(self.__dict__)
        state_keys += [i for i in self.__dir__() if not i.startswith("_")]
        self._leaves = {"event" : {}}
        for i in set(state_keys):
            if i == "clone": continue
            try: v = getattr(self, i)
            except AttributeError: continue
            if type(v).__name__ == "builtin_function_or_method": continue
            if type(v).__name__ == "method": continue
            state.update({i : v})
        return state

    def __setstate__(self, dict inpt) -> None:
        cdef str i
        for i in inpt:
            try: setattr(self, i, inpt[i])
            except (IndexError, KeyError): pass

    @property
    def __interpret__(self) -> dict:
        cdef str i
        cdef list exl = ["CommitHash", "Deprecated"]
        for i, v in zip(self.__dict__, self.__dict__.values()):
            if isinstance(v, list): continue
            if isinstance(v, dict): continue
            if i in exl: continue
            self._leaves["event"][i] = v

        for i in self._Objects:
            if self._Objects[i]._init != False: self._Objects[i] = self._Objects[i]()
            self._leaves[i] = self._Objects[i].__interpret__

        cdef list col = []
        col += self.Branches
        for i in self._leaves: col += list(self._leaves[i].values())
        self.Leaves += col
        return self._leaves

    @__interpret__.setter
    def __interpret__(self, dict val):
        cdef str i
        for i in val: setattr(self, i, val[i])

    def __compiler__(self, inpt: Union[dict]):
        cdef str i, k, tr
        cdef dict val, _inpt
        cdef list Obj = list(self._Objects) + ["event"]
        cdef EventTemplate ev
        cdef list out = []

        for tr in self._Trees:
            _inpt = {k.split(tr + "/")[-1] : inpt[k] for k in inpt if tr in k}
            if len(_inpt) == 0: continue
            ev = self.clone()
            ev.__interpret__
            ev.Tree = tr
            for i in Obj:
                val = ev._leaves[i] if i == "event" else ev._Objects[i].__interpret__
                val = {k : _inpt[val[k]] for k in val if val[k] in _inpt}
                if len(val) == 0 and i in ev._Objects:
                    del ev._Objects[i]
                    continue
                if i == "event":
                    ev.__interpret__ = val
                    continue
                ev._Objects[i].__interpret__ = val
                setattr(ev, i, {p : ev._Objects[i].Children[p] for p in range(len(ev._Objects[i].Children))})
                obj = ev._Objects[i]
                del obj

            out.append(ev)
            ev._Objects = {}
            inpt = {k : inpt[k] for k in inpt if tr not in k}
            if ev.index == -1: ev.index = inpt["EventIndex"]
            if not inpt["MetaData"].init: root = inpt["ROOT"]
            else:
                root, dataset = inpt["MetaData"].GetDAOD(ev.index)
                root = dataset + "/" + root
            ev.hash = root
        del inpt
        return out

    def CompileEvent(self): pass

    def clone(self):
        v = self.__new__(self.__class__)
        v.__init__()
        return v

    @property
    def index(self) -> int: return self.ptr.index

    @index.setter
    def index(self, val: Union[int, str]):
        if isinstance(val, int): self.ptr.index = val
        elif isinstance(val, str): self._leaves["event"]["index"] = val

    @property
    def weight(self) -> float: return self.ptr.weight

    @weight.setter
    def weight(self, val: Union[str, float]):
        if isinstance(val, str): self._leaves["event"]["weight"] = val
        else: self.ptr.weight = <double>val

    @property
    def Tree(self) -> str: return self.ptr.tree.decode("UTF-8")

    @property
    def Trees(self) -> list: return self._Trees

    @property
    def Branches(self) -> list: return self._Branches

    @property
    def Leaves(self) -> list: return self._Leaves

    @property
    def Objects(self) -> dict: return self._Objects

    @Tree.setter
    def Tree(self, str val):
        self.ptr.tree = val.encode("UTF-8")

    @Trees.setter
    def Trees(self, val: Union[str, list]):
        if isinstance(val, str): val = [val]
        self._Trees += val

    @Branches.setter
    def Branches(self, val: Union[str, list]):
        if isinstance(val, str): val = [val]
        self._Branches += val

    @Leaves.setter
    def Leaves(self, val: Union[str, list]):
        if isinstance(val, str): val = [val]
        self._Leaves += val

    @property
    def hash(self) -> str: return self.ptr.Hash().decode("UTF-8")

    @hash.setter
    def hash(self, str val): self.ptr.Hash(val.encode("UTF-8"))

    @property
    def Deprecated(self) -> bool: return self.ptr.deprecated

    @Deprecated.setter
    def Deprecated(self, bool val): self.ptr.deprecated = val

    @property
    def _init(self) -> bool: return True

    @Objects.setter
    def Objects(self, val: Union[dict]): self._Objects = val


