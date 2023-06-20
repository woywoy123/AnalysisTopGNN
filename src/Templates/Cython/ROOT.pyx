#distutils: language = c++
#cython: language_level=3

from ROOT cimport CySampleTracer, CyROOT, CyEvent
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map, pair
from libcpp cimport bool
import h5py
import os
import sys
import shutil
import pickle
import codecs
from tqdm import tqdm
from typing import Union, Dict, List
from AnalysisG.Tools import Code, Threading
from AnalysisG.Notification.Notification import Notification
from torch_geometric.loader import DataListLoader
from torch_geometric.data import Batch
import torch

cdef class Event:
    cdef CyEvent* ptr
    cdef public list _instance
    cdef public bool _demanded
    def __cinit__(self):
        self.ptr = NULL
        self._demanded = False

    def __init__(self): self._instance = []
    def _wrap(self, val): self._instance.append(val)
    def __setstate__(self, inpt): setattr(self, "_instance", inpt["_instance"])
    def __getattr__(self, attr):
        self.demand()
        try: return getattr(self._instance[0], attr)
        except AttributeError: pass
        try: return getattr(self._instance[1], attr)
        except: pass
        raise AttributeError

    def __getstate__(self):
        out = {}
        out["_instance"] = self._instance
        return out

    def __eq__(self, other) -> bool:
        if not issubclass(other.__class__, Event): return False
        if self.hash != other.hash: return False
        if self.Tree != other.Tree: return False
        try: return self.Event == other.Event
        except AttributeError: pass
        try: return self.Graph == other.Graph
        except AttributeError: pass
        return False

    def demand(self) -> None:
        if self._demanded: return
        try: self._instance[0] = pickle.loads(codecs.decode(self._instance[0], "base64"))
        except TypeError: pass
        self._demanded = True
        return

    @property
    def index(self) -> int: return self.ptr.EventIndex

    @property
    def Tree(self) -> str: return self.ptr.Tree.decode("UTF-8")

    @property
    def Graph(self) -> bool: return self.ptr.Graph

    @property
    def Event(self) -> bool: return self.ptr.Event

    @property
    def hash(self) -> str: return self.ptr.hash.decode("UTF-8")

    @property
    def ROOT(self) -> str: return self.ptr.ROOT.decode("UTF-8")

    @property
    def CachePath(self) -> str: return self.ptr.ROOTFile.CachePath.decode("UTF-8")

    @property
    def TrainMode(self) -> str: return self.ptr.TrainMode.decode("UTF-8")

    @TrainMode.setter
    def TrainMode(self, val) -> str: self.ptr.TrainMode = val.encode("UTF-8")

    @property
    def CachedGraph(self) -> bool: return self.ptr.CachedGraph

    @property
    def CachedEvent(self) -> bool: return self.ptr.CachedEvent

    @property
    def num_nodes(self) -> int: return self.ptr.num_nodes

cdef class SampleTracer:
    cdef CySampleTracer* ptr
    cdef vector[string] _itv
    cdef map[string, string] _HashMeta
    cdef dict HashMeta
    cdef int _its
    cdef int _ite
    cdef str OutDir
    cdef bool _EventCache
    cdef bool _DataCache
    cdef str _SampleName
    cdef dict _Codes
    cdef dict _Files
    cdef dict _DataBatchCache

    def __cinit__(self):
        self.ptr = new CySampleTracer()
        self.HashMeta = {}
        self.OutDir = os.getcwd()
        self._SampleName = ""
        self._Codes = {}
        self._Files = {}
        self._DataBatchCache = {}

    def __dealloc__(self): del self.ptr
    def __init__(self): pass

    def __contains__(self, str key) -> bool:
        if key.endswith(".root"): key = os.path.abspath(key)
        if self.ptr.ContainsROOT(key.encode("UTF-8")): return True
        if self.ptr.ContainsHash(key.encode("UTF-8")): return True
        if key in self.HashMeta: return True
        return False

    def __getitem__(self, str key):
        cdef string _key = key.encode("UTF-8")
        cdef string _meta
        cdef str daod, meta
        cdef list out = []

        cdef vector[string] v = self.ptr.ROOTtoHashList(_key)
        if v.size() == 0 and self.ptr.ContainsHash(_key): v = [_key]
        if v.size() > 0:
            for _key in v:
                ev = Event()
                ev.ptr = self.ptr.HashToEvent(_key)
                ev._wrap(ev.ptr.pkl)
                out.append(ev)

                _meta = self._HashMeta[_key]
                if _meta.size() == 0: pass
                else: ev._wrap(self.HashMeta[_meta.decode("UTF-8")]); continue

                meta = (ev.ptr.ROOTFile.SourcePath + ev.ptr.ROOTFile.Filename).decode("UTF-8")
                for daod in self.HashMeta:
                    M = self.HashMeta[daod]
                    if not M.MatchROOTName(meta): continue
                    self._HashMeta[_key] = daod.encode("UTF-8")
                    ev._wrap(M)

        if len(out) == 1: return out[0]
        elif len(out) > 1: return out

        if key.endswith(".root"): key = os.path.abspath(key)
        if key in self.HashMeta:
            for daod in self.HashMeta[key].Files:
                try: out += self[self.HashMeta[key].thisSet + daod]
                except: continue
            return out
        return out

    def __len__(self) -> int:
        if self.DataCache and not self.EventCache: self._itv = self.ptr.GetCacheType(False, True)
        elif self.EventCache and not self.DataCache: self._itv = self.ptr.GetCacheType(True, False)
        else: self._itv = self.ptr.HashList()
        self.ptr.length = self._itv.size()
        return self.ptr.length

    def __add__(self, other) -> SampleTracer:
        if isinstance(other, int): return self
        if isinstance(self, int): return other
        cdef SampleTracer s = self
        cdef SampleTracer o = other
        cdef SampleTracer t = self.clone
        del t.ptr
        t.ptr = s.ptr[0] + o.ptr
        t.HashMeta.update(s.HashMeta)
        t.HashMeta.update(o.HashMeta)
        t._Codes.update(s._Codes)
        t._Codes.update(o._Codes)
        return t

    def __iadd__(self, other):
        cdef SampleTracer s = self
        cdef SampleTracer o = other
        s.ptr = s.ptr[0] + o.ptr
        s.HashMeta.update(o.HashMeta)
        s._Codes.update(o._Codes)
        s.Threads = <int>self.Threads
        return s

    @property
    def clone(self):
        v = self.__new__(self.__class__)
        v.__init__()
        return v

    def FastHashSearch(self, list hashes) -> dict:
        cdef string key
        cdef bool fnd
        cdef vector[string] v = [i.encode("UTF-8") for i in hashes]
        return {key.decode("UTF-8") : fnd for key, fnd in self.ptr.FastSearch(v)}

    def HashToROOT(self, str key) -> str: return self._HashMeta[key.encode("UTF-8")].decode("UTF-8")

    @property
    def GetDataCacheHashes(self) -> list:
        cdef string i
        cdef vector[string] v = self.ptr.GetCacheType(False, True)
        return [i.decode("UTF-8") for i in v]

    @property
    def GetEventCacheHashes(self) -> list:
        cdef string i
        cdef vector[string] v = self.ptr.GetCacheType(True, False)
        return [i.decode("UTF-8") for i in v]

    @property
    def DataCacheLen(self) -> int: return self.ptr.GetCacheType(False, True).size()

    @property
    def EventCacheLen(self) -> int: return self.ptr.GetCacheType(True, False).size()

    def _decoder(self, str inpt): return pickle.loads(codecs.decode(inpt.encode("UTF-8"), "base64"))

    def _encoder(self, inpt) -> str: return codecs.encode(pickle.dumps(inpt), "base64").decode()

    def _rebuild_code(self, str pth, ref) -> None:
        cdef str k
        try: os.makedirs(pth)
        except FileExistsError: sys.path.append(pth); return
        for k in ref["code"].attrs:
            Code = self._decoder(ref["code"].attrs[k])
            k = Code._File.split("/")[-1]
            mk = open(pth + k, "w")
            mk.write(Code._FileCode)
            mk.close()
        sys.path.append(pth)

    @property
    def Threads(self) -> int: return self.ptr.Threads

    @property
    def chnk(self) -> int: return self.ptr.ChunkSize

    @Threads.setter
    def Threads(self, int val): self.ptr.Threads = val

    @chnk.setter
    def chnk(self, int val): self.ptr.ChunkSize = val

    @property
    def OutputDirectory(self): return self.OutDir

    @OutputDirectory.setter
    def OutputDirectory(self, str val): self.OutDir = val

    @property
    def EventCache(self) -> bool: return self._EventCache

    @EventCache.setter
    def EventCache(self, bool val): self._EventCache = val

    @property
    def DataCache(self) -> bool: return self._DataCache

    @DataCache.setter
    def DataCache(self, bool val): self._DataCache = val

    @property
    def SampleName(self) -> str: return self._SampleName

    @SampleName.setter
    def SampleName(self, str val): self._SampleName = val

    @property
    def todict(self) -> dict: return {i.hash : i for i in self}

    @property
    def tolist(self) -> list: return [i for i in self]

    @property
    def Files(self) -> dict: return self._Files

    @Files.setter
    def Files(self, dict val): self._Files = val

    @property
    def len(self) -> int: return self.ptr.length

    def AddEvent(self, dict Events):
        cdef str i, p
        cdef dict x
        cdef list hashes = list(Events)
        if len(self._Codes) == 0 and len(hashes) != 0:
            p = hashes[0]
            cl = Code(pickle.loads(Events[p]["pkl"]))
            x = cl.clone.Objects
            self._Codes.update({t._Name : t.purge for t in [Code(x[p]) for p in x]})
            self._Codes[cl._Name] = cl.purge
            del cl

        x = self.FastHashSearch(hashes)
        for i in x:
            if x[i]: continue
            _ev = new CyEvent()
            _ev.pkl = codecs.encode(Events[i]["pkl"], "base64")
            _ev.Tree = Events[i]["Tree"].encode("UTF-8")
            _ev.hash = i.encode("UTF-8")
            _ev.ROOT = Events[i]["ROOT"].encode("UTF-8")
            _ev.EventIndex = Events[i]["index"]
            _ev.Event = True
            self.ptr.AddEvent(_ev)
            self.HashMeta[Events[i]["Meta"].ROOTName] = Events[i]["Meta"]

    def AddGraph(self, Events):
        cdef int i, num_nodes;
        cdef str _hash
        cdef CyEvent* event;
        for i in range(len(Events)):
            _hash, evnt, num_nodes = Events[i]
            if evnt is None: continue
            event = self.ptr.HashToEvent(_hash.encode("UTF-8"))
            event.Graph = True
            event.Event = False
            event.num_nodes = num_nodes
            event.pkl = codecs.encode(evnt, "base64")

    @property
    def DumpTracer(self):

        cdef pair[string, CyROOT*] root
        cdef pair[string, CyEvent*] event
        cdef CyROOT* r
        cdef CyEvent* e
        cdef str _meta
        cdef str out

        for root in self.ptr._ROOTMap:
            r = root.second

            out = self.OutDir + "/Tracer/" + r.CachePath.decode("UTF-8")
            try: os.makedirs("/".join(out.split("/")[:-1]))
            except FileExistsError: pass

            f = h5py.File(out + ".hdf5", "a")
            try: ref_s = f.create_dataset("SampleNames", (1), dtype = h5py.ref_dtype)
            except ValueError: ref_s = f["SampleNames"]
            if self._SampleName != "": ref_s.attrs[self._SampleName] = True

            for _meta in self.HashMeta:
                if not self.HashMeta[_meta].MatchROOTName(root.first.decode("UTF-8")): continue
                try: ref_s = f.create_dataset("MetaData", (1), dtype = h5py.ref_dtype)
                except ValueError: ref_s = f["MetaData"]
                ref_s.attrs[_meta] = self._encoder(self.HashMeta[_meta])

            for event in r.HashMap:
                e = event.second
                try: ref = f.create_dataset(event.first.decode("UTF-8"), (1), dtype = h5py.ref_dtype)
                except ValueError: ref = f[event.first.decode("UTF-8")]

                ref.attrs["Tree"] = e.Tree
                ref.attrs["TrainMode"] = e.TrainMode
                ref.attrs["Hash"] = e.hash
                ref.attrs["ROOT"] = e.ROOT
                ref.attrs["EventIndex"] = e.EventIndex
                ref.attrs["CachedEvent"] = e.CachedEvent
                ref.attrs["CachedGraph"] = e.CachedGraph
                ref.attrs["num_nodes"] = e.num_nodes

            f.close()

    @property
    def DumpEvents(self):

        cdef CyEvent* e
        cdef CyROOT* r
        cdef pair[string, CyROOT*] p
        cdef str out, l
        cdef str file = ""

        try: os.mkdir(self.OutDir)
        except FileExistsError: pass

        l = "TRACER::DUMPING EVENTS (" + ("DataCache" if self._DataCache else "EventCache") + ")"
        _, bar = self._MakeBar(self.ptr._ROOTHash.size(), l)
        for p in self.ptr._ROOTHash:
            r = p.second
            e = self.ptr.HashToEvent(p.first)

            bar.update(1)
            if e.CachedEvent and e.Event: continue
            if e.CachedGraph and e.Graph: continue
            if e.pkl.size() == 0: continue

            if e.Event:   out = self.OutDir + "/EventCache/"
            elif e.Graph: out = self.OutDir + "/DataCache/"
            else: continue

            out += r.CachePath.decode("UTF-8")
            try: os.makedirs("/".join(out.split("/")[:-1]))
            except FileExistsError: pass

            if file != out: f = h5py.File(out + ".hdf5", "a")
            try: ref = f.create_dataset(p.first.decode("UTF-8"), (1), dtype = h5py.ref_dtype)
            except ValueError: ref = f[p.first.decode("UTF-8")]

            if e.Event: e.CachedEvent = True
            elif e.Graph: e.CachedGraph = True
            else: continue

            ref.attrs["Event"] = e.pkl.decode("UTF-8")
            file = out if file != "" else file
            if file != out:
                try: ref = f.create_dataset("code", (1), dtype = h5py.ref_dtype)
                except ValueError: ref = f["code"]
                for l in self._Codes: ref.attrs[l] = self._encoder(self._Codes[l])
                f.close()
        self.DumpTracer

    @property
    def RestoreTracer(self):
        cdef str i, k
        cdef CyROOT* R
        cdef CyEvent* E
        cdef dict maps
        cdef list get

        try: get = [self.OutDir + "/Tracer/" + i for i in os.listdir(self.OutDir + "/Tracer/")]
        except FileNotFoundError: return
        get = [i + "/" + k for i in get for k in os.listdir(i) if k.endswith(".hdf5")]

        for i in get:
            try: f = h5py.File(i, "r")
            except: continue

            try:
                if self._SampleName == "": raise KeyError
                try: f["SampleNames"].attrs[self._SampleName]
                except KeyError: continue
            except KeyError: pass
            maps = {i : self._decoder(f["MetaData"].attrs[i]) for i in f["MetaData"].attrs}

            if len(self._Files) == 0: pass
            elif len([i for i in self._Files for k in self._Files[i] if i + "/" + k in maps]) == 0: continue

            self.HashMeta.update(maps)
            maps = self.FastHashSearch([k for k in f if k != "SampleNames" and k != "code" and k != "MetaData"])

            for i in maps:
                if maps[i]: continue
                ref = f[i]
                E = new CyEvent()
                E.Tree = ref.attrs["Tree"].encode("UTF-8")
                E.TrainMode = ref.attrs["TrainMode"].encode("UTF-8")
                E.ROOT = ref.attrs["ROOT"].encode("UTF-8")
                E.EventIndex = ref.attrs["EventIndex"]
                E.CachedEvent = ref.attrs["CachedEvent"]
                E.CachedGraph = ref.attrs["CachedGraph"]
                E.num_nodes = ref.attrs["num_nodes"]
                E.Hash()
                self.ptr.AddEvent(E)

    @property
    def RestoreEvents(self) -> None:

        cdef pair[string, CyROOT*] c
        cdef pair[string, CyEvent*] e
        cdef CyROOT* r_
        cdef CyEvent* e_
        cdef str get
        cdef bool DataCache, EventCache

        _notify = Notification(3, "TRACER")
        for c in self.ptr._ROOTMap:
            DataCache = self._DataCache
            EventCache = self._EventCache
            r_ = c.second

            if DataCache:  get = self.OutDir + "/DataCache/" + r_.CachePath.decode("UTF-8") + ".hdf5"
            if DataCache: DataCache = os.path.isfile(get)
            EventCache = True if not DataCache else False

            if EventCache: get = self.OutDir + "/EventCache/" + r_.CachePath.decode("UTF-8") + ".hdf5"
            if EventCache: EventCache = os.path.isfile(get)
            DataCache = True if not EventCache else False

            if DataCache:  get = self.OutDir + "/DataCache/" + r_.CachePath.decode("UTF-8") + ".hdf5"

            try: f = h5py.File(get, "r")
            except: continue
            if EventCache: self._rebuild_code(get.replace(".hdf5", "/"), f)

            get = "TRACER::READING EVENTS (" + ("DataCache" if DataCache else "EventCache") + "): "
            _, bar = self._MakeBar(r_.HashMap.size(), get + c.first.decode("UTF-8").split("/")[-1])
            for e in r_.HashMap:
                bar.update(1)
                e_ = e.second
                if e_ is NULL: continue
                if not e_.CachedGraph and not e_.CachedEvent: continue
                e_.pkl = f[e.first.decode("UTF-8")].attrs["Event"].encode("UTF-8")
                e_.Event = EventCache; e_.Graph = DataCache

    def RestoreTheseHashes(self, list hashes = []) -> None:
        self.ptr.length = 0
        cdef str i
        cdef CyEvent* e_
        cdef string hash_
        cdef bool loaded
        self._itv = [i.encode("UTF-8") for i in hashes] if len(hashes) > 0 else self._itv
        for hash_ in self._itv:
            e_ = self.ptr.HashToEvent(hash_)
            if e_ is NULL: continue
            self.ptr.length += 1
            loaded = e_.pkl.size() > 0
            if loaded and self._EventCache and e_.Event: continue
            if loaded and self._DataCache and e_.Graph: continue
            i = self.OutDir
            i += "/DataCache/" if self._DataCache else "/EventCache/"
            i += e_.ROOTFile.CachePath.decode("UTF-8") + ".hdf5"
            try: f = h5py.File(i, "r")
            except: continue
            if self._EventCache: self._rebuild_code(i.replace(".hdf5", "/"), f)

            e_.pkl = f[hash_.decode("UTF-8")].attrs["Event"].encode("UTF-8")
            e_.Event = self._EventCache; e_.Graph = self._DataCache

    def ForceTheseHashes(self, inpt: Union[Dict, List]) -> None:
        cdef str i
        inpt = inpt if isinstance(inpt, list) else list(inpt)
        self._itv = [i.encode("UTF-8") for i in inpt]
        self._ite = self._itv.size()
        self.ptr.length = self._ite

    def MarkTheseHashes(self, inpt: Union[Dict, list], str label) -> None:
        inpt = inpt if isinstance(inpt, list) else list(inpt)
        cdef str i
        cdef vector[string] smpl = [i.encode("UTF-8") for i in inpt]
        cdef string _i
        cdef CyEvent* ev
        cdef string lab = label.encode("UTF-8")
        for _i in smpl:
            if not self.ptr.ContainsHash(_i): continue
            ev = self.ptr.HashToEvent(_i)
            ev.TrainMode = lab

    @property
    def SortNumNodes(self):
        cdef map[int, vector[string]] nodes_hash
        cdef pair[int, vector[string]] _n
        cdef string i
        for i in self._itv: nodes_hash[self.ptr.HashToEvent(i).num_nodes].push_back(i)
        self._itv.clear()
        for _n in nodes_hash: self._itv.insert(self._itv.end(), _n.second.begin(), _n.second.end())

    @property
    def GPUMemory(self) -> float:
        cdef tuple v = torch.cuda.mem_get_info()
        return (1 - v[0]/v[1])*100

    @property
    def FlushBatchCache(self):
        cdef str key
        cdef dict tmp = {}
        for key in list(self._DataBatchCache):
            if self._DataBatchCache[key].i.device == "cpu":
                d = self._DataBatchCache[key]
                del d
                continue

            if self.GPUMemory < 80: tmp[key] = self._DataBatchCache[key]
            else: del self._DataBatchCache[key]; torch.cuda.empty_cache()
        self._DataBatchCache = tmp

    def FlushTheseHashes(self, inpt: Union[List] = []):
        cdef str i
        cdef vector[string] hashes
        cdef string hash_
        cdef CyEvent* e_
        hashes = self._itv if len(inpt) == 0 else [i.encode("UTF-8") for i in inpt]
        for hash_ in hashes:
            e_ = self.ptr.HashToEvent(hash_)
            e_.pkl = "".encode("UTF-8")

    def BatchTheseHashes(self, list hashes, label: Union[int, str], str device):
        if label in self._DataBatchCache: return self._DataBatchCache[label]
        cdef str hash_
        self._itv = [hash_.encode("UTF-8") for hash_ in hashes]
        self.ptr.length = self._itv.size()
        self.RestoreTheseHashes()
        self._DataBatchCache[label] = Batch().from_data_list([i.clone().to(device) for i in self])
        if self._DataCache: self.FlushTheseHashes()
        return self._DataBatchCache[label]

    def _MakeBar(self, inpt: Union[int], CustTitle: Union[None, str] = None):
        _dct = {}
        _dct["desc"] = f'Progress {self.Caller}' if CustTitle is None else CustTitle
        _dct["leave"] = True
        _dct["colour"] = "GREEN"
        _dct["dynamic_ncols"] = True
        _dct["total"] = inpt
        return (None, tqdm(**_dct))

    def __preiteration__(self): return False

    def __iter__(self):
        if self.len == 0: len(self)
        if self.__preiteration__(): return self
        self._its = 0
        self._ite = self._itv.size()
        self.ptr.length = self._ite
        return self

    def __next__(self):
        if self._its == self._ite: raise StopIteration
        cdef str i, meta
        cdef string _hash, _meta
        cdef CyEvent* event = NULL
        _hash = self._itv[self._its]
        self._its += 1

        if _hash.size() != 0: event = self.ptr.HashToEvent(_hash)
        else: return self.__next__()
        if event == NULL: return self.__next__()

        ev = Event()
        ev.ptr = event
        ev._wrap(ev.ptr.pkl)

        _meta = self._HashMeta[_hash]
        if _meta.size() == 0: meta = (event.ROOTFile.SourcePath + event.ROOTFile.Filename).decode("UTF-8")
        else: ev._wrap(self.HashMeta[_meta.decode("UTF-8")]); return ev

        for i in self.HashMeta:
            M = self.HashMeta[i]
            if not M.MatchROOTName(meta): continue
            self._HashMeta[_hash] = i.encode("UTF-8")
            ev._wrap(M)
        return ev

