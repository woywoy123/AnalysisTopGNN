# distuils: language = c++
# cython: language_level = 3

from AnalysisG._cmodules.MetaData import MetaData
from typing import Union

from cyevent cimport CyEventTemplate
from cytypes cimport meta_t, event_t

from libcpp.string cimport string
from libcpp.map cimport map, pair
from libcpp cimport bool

cdef string enc(str val): return val.encode("UTF-8")
cdef str env(string val): return val.decode("UTF-8")

cdef class EventTemplate:
    cdef CyEventTemplate* ptr
    cdef event_t* ev
    cdef dict Objects
    cdef meta

    def __cinit__(self):
        self.ptr = new CyEventTemplate()
        cdef str x = self.__class__.__name__
        self.ev = &(self.ptr.event)
        self.ptr.set_event_name(self.ev, enc(x))
        self.meta = MetaData()
        self.Objects = {}

    def __init__(self): pass
    def __dealloc__(self): del self.ptr
    def __name__(self) -> str: return env(self.ev.event_name)
    def __hash__(self) -> int: return int(self.hash[:8], 0)

    def __eq__(self, other) -> bool:
        if not self.is_self(other): return False
        cdef EventTemplate o = other
        return self.ptr[0] == o.ptr[0]

    def __getstate__(self) -> tuple:
        cdef str key
        cdef dict pkl = {}
        for key in list(self.__dict__):
            pkl[key] = self.__dict__[key]
        return (pkl, self.ptr.Export())

    def __setstate__(self, tuple inpt):
        cdef str key
        self.ptr.Import(inpt[1])
        for key in inpt[0]:
            try: self.__dict__[key] = inpt[0][key]
            except KeyError: setattr(self, key, inpt[0][key])

    def __getleaves__(self) -> dict:
        cdef str i
        cdef dict leaves = {}
        cdef pair[string, string] x
        for x in self.ptr.leaves: leaves[env(x.first)] = env(x.second)
        for i, v in zip(self.__dict__, self.__dict__.values()):
            if not isinstance(v, str): continue
            leaves[i] = v
        leaves = {"event" : leaves}
        for i in self.Objects:
            try: self.Objects[i] = self.Objects[i]()
            except TypeError: pass
            leaves[i] = self.Objects[i].__getleaves__()

        self.Leaves = []
        for i in leaves: self.Leaves += list(leaves[i].values())
        return leaves

    def __compiler__(self, inpt: Union[dict]):
        cdef EventTemplate event = self.clone()
        meta = inpt["MetaData"]

        cdef int x
        cdef list sub_keys
        cdef dict inpt_map = {}
        cdef dict var_leaf
        cdef str tree, key, typ, k, v

        for tree in self.Trees:
            for key in inpt:
                sub_keys = key.split("/")
                typ = sub_keys[0]
                if tree not in typ: continue
                if len(sub_keys) <= 1: continue
                if tree not in inpt_map: inpt_map[tree] = {}

                inpt_map[tree][sub_keys[-1]] = inpt[key]

            if tree not in inpt_map: continue
            var_leaf = self.__getleaves__()
            sub_keys = list(inpt_map[tree])
            for typ in var_leaf:
                if not len(sub_keys): break
                for v, k in var_leaf[typ].items():
                    for x in range(len(sub_keys)):
                        if k != sub_keys[x]: continue
                        if typ not in var_leaf: var_leaf[typ] = {}
                        key = sub_keys.pop(x)
                        var_leaf[typ][v] = inpt_map[tree][key]
                        break
                if typ != "event":
                    try: obj = event.Objects[typ]()
                    except: obj = event.Objects[typ]
                    inpt_map[tree][typ] = obj.__build__(var_leaf[typ])
                    continue

                obj = self.clone(meta.__getstate__())
                obj.__build__(var_leaf[typ])
                obj.Tree = tree
                if obj.index == -1: obj.index = inpt["EventIndex"]
                else: meta.eventNumber = obj.index
                obj.ROOT = meta.DatasetName + "/" + meta.DAOD.split("/")[-1]
                obj.hash
                inpt_map[tree][typ] = obj

            for typ in inpt_map[tree]:
                if typ == "event": continue
                setattr(inpt_map[tree]["event"], typ, inpt_map[tree][typ])

            inpt_map[tree] = inpt_map[tree]["event"]
        return list(inpt_map.values())

    def __build__(self, dict variables):
        cdef str keys
        for keys in variables:
            try: variables[keys] = variables[keys].tolist()
            except AttributeError: pass

            try: variables[keys] = variables[keys].pop()
            except AttributeError: pass

            setattr(self, keys, variables[keys])

    def is_self(self, inpt) -> bool:
        if isinstance(inpt, EventTemplate): return True
        return issubclass(inpt.__class__, EventTemplate)

    def clone(self, meta = None) -> EventTemplate:
        v = self.__class__
        v = v()
        if meta is None: return v
        v.ImportMetaData(meta)
        return v

    def CompileEvent(self): pass

    def ImportMetaData(self, meta_t meta):
        self.ptr.ImportMetaData(meta)
        self.meta.__setstate__(meta)

    @property
    def Export(self) -> event_t:
        return self.ptr.Export()

    @property
    def index(self) -> int:
        return self.ev.event_index

    @index.setter
    def index(self, val: Union[str, double]):
        try: self.ev.event_index = val
        except TypeError: self.ptr.addleaf(b'index', enc(val))

    @property
    def weight(self) -> double:
        return self.ev.weight

    @weight.setter
    def weight(self, val: Union[str, double]):
        try: self.ev.weight = val
        except TypeError: self.ptr.addleaf(b'weight', enc(val))

    @property
    def deprecated(self) -> bool:
        return self.ev.deprecated

    @deprecated.setter
    def deprecated(self, bool val):
        self.ev.deprecated = val

    @property
    def CommitHash(self) -> str:
        return env(self.ev.commit_hash)

    @CommitHash.setter
    def CommitHash(self, str val):
        self.ev.commit_hash = enc(val)

    @property
    def Tag(self) -> str:
        return env(self.ev.event_tagging)

    @Tag.setter
    def Tag(self, str val):
        self.ev.event_tagging = enc(val)

    @property
    def Tree(self) -> str:
        return env(self.ev.event_tree)

    @Tree.setter
    def Tree(self, str val):
        self.ev.event_tree = enc(val)

    @property
    def Trees(self) -> list:
        cdef pair[string, string] x
        return [env(x.first) for x in self.ptr.trees]

    @Trees.setter
    def Trees(self, val: Union[str, list]):
        cdef str i
        if isinstance(val, str):
            self.ptr.addtree(enc(val), b'Tree')
        elif isinstance(val, list):
            for i in val: self.Trees = i
        else: pass

    @property
    def Branches(self) -> list:
        cdef pair[string, string] x
        return [env(x.first) for x in self.ptr.branches]

    @Branches.setter
    def Branches(self, val: Union[str, list]):
        if isinstance(val, str):
            self.ptr.addbranch(enc(val), b'Branch')
        elif isinstance(val, list):
            for i in val: self.Branches = i
        else: pass

    @property
    def cached(self) -> bool:
        return self.ev.cached

    @cached.setter
    def cached(self, bool val) -> bool:
        self.ev.cached = val

    @property
    def ROOT(self) -> str:
        return env(self.ev.event_root)

    @ROOT.setter
    def ROOT(self, str val):
        self.ev.event_root = enc(val)

    @property
    def hash(self) -> str:
        return env(self.ptr.Hash())

    @property
    def Objects(self) -> dict:
        return self.Objects

    @Objects.setter
    def Objects(self, val):
        if not isinstance(val, dict): val = {"title" : val}
        self.Objects = val

    @property
    def Event(self) -> bool:
        return self.ptr.is_event

    @property
    def EventName(self) -> str:
        return env(self.ev.event_name)

    @property
    def meta(self):
        return self.meta
