# distuils: language = c++
# cython: language_level = 3

from cysampletracer cimport CySampleTracer, CyBatch, HDF5_t
from cytools cimport *

from cyevent cimport CyEventTemplate
from cygraph cimport CyGraphTemplate
from cyselection cimport CySelectionTemplate

from cytypes cimport event_t, graph_t, selection_t, code_t
from cytypes cimport tracer_t, batch_t, meta_t, settings_t, export_t

from AnalysisG.Tools import Code, Threading
from cycode cimport CyCode

from AnalysisG._cmodules.SelectionTemplate import SelectionTemplate
from AnalysisG._cmodules.EventTemplate import EventTemplate
from AnalysisG._cmodules.GraphTemplate import GraphTemplate
from AnalysisG._cmodules.MetaData import MetaData

from cython.operator cimport dereference
from cython.parallel cimport prange
from cython cimport dict

from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.map cimport map, pair
from libcpp cimport bool

from typing import Union
from tqdm import tqdm
import psutil
import torch
import pickle
import h5py
import os

def _check_h5(f, str key):
    try: return f.create_dataset(key, (1), dtype = h5py.ref_dtype)
    except ValueError: return f[key]

def _check_sub(f, str key):
    try: return f.create_group(key)
    except ValueError: return f[key]

cdef void tracer_dump(f, export_t* state, string root_name):
    cdef pair[string, code_t] itc
    ref_ = _check_h5(f, "code")
    for itc in state.hashed_code: ref_.attrs[itc.first] = _encoder(itc.second)

    cdef pair[string, string] itr
    ref_ = _check_h5(f, "link_event_code")
    for itr in state.link_event_code: ref_.attrs[itr.first] = itr.second

    ref_ = _check_h5(f, "link_graph_code")
    for itr in state.link_graph_code: ref_.attrs[itr.first] = itr.second

    ref_ = _check_h5(f, "link_selection_code")
    for itr in state.link_selection_code: ref_.attrs[itr.first] = itr.second

    tracer_link(f, &state.event_name_hash, &state.event_dir, "event", root_name)
    tracer_link(f, &state.graph_name_hash, &state.graph_dir, "graph", root_name)
    tracer_link(f, &state.selection_name_hash, &state.selection_dir, "selection", root_name)

cdef void tracer_HDF5(ref, map[string, HDF5_t]* data, string type_key):
    cdef str hash_, root_, type_, path_

    cdef HDF5_t* data_tmp
    for type_ in ref:
        if not type_.startswith(env(type_key) + ":"): continue
        path_ = ref[env(type_key) + "_dir"].attrs[type_.split(":")[-1]]
        for hash_, root_ in ref[type_].attrs.items():
            data_tmp = &dereference(data)[enc(hash_)]
            data_tmp.root_name = enc(root_)
            data_tmp.cache_path[enc(path_)] = type_key


cpdef dump_objects(inpt, _prgbar):
    lock, bar = _prgbar
    cdef int i
    cdef str out_path = inpt[0][0]
    cdef str short_ = inpt[0][1]
    cdef list prc = inpt[0][2]

    cdef string hash_
    cdef event_t ev
    cdef graph_t gr
    cdef selection_t sel

    f = h5py.File(out_path, "a")
    bar.total = len(prc)
    bar.refresh()
    for i in range(bar.total):
        dt = _check_sub(f, env(prc[i]["event_hash"]))
        ref = _check_h5(dt, short_)
        if prc[i]["event"]: ev = prc[i]; save_event(ref, &ev)
        elif prc[i]["graph"]: gr = prc[i]; save_graph(ref, &gr)
        elif prc[i]["selection"]: sel = prc[i]; save_selection(ref, &sel)
        else: continue
        with lock: bar.update(1)
    f.close()
    del f
    return [None]

cpdef fetch_objects(list inpt, _prgbar):
    lock, bar = _prgbar
    cdef int i
    cdef str key
    cdef str hash_
    cdef str read_path = env(inpt[0][0])
    cdef str type_ = inpt[0][1]
    cdef list hashes = inpt[0][2]
    cdef dict output = {}

    bar.total = len(hashes)
    bar.refresh()
    f = h5py.File(read_path, "r")
    cdef event_t ev
    cdef graph_t gr
    cdef selection_t sel

    for i in range(bar.total):
        hash_ = env(hashes[i])
        dt = f[hash_]
        for key in dt.keys():
            if type_ == "Event":
                restore_event(dt[key], &ev)
                output[hash_] = ev

            elif type_ == "Graph":
                restore_graph(dt[key], &gr)
                output[hash_] = gr

            elif type_ == "Selection":
                restore_selection(dt[key], &sel)
                output[hash_] = sel

            else: continue
            with lock: bar.update(1)
    f.close()
    del f
    return [[enc(read_path), output]]




cdef class Event:
    cdef _event
    cdef _graph
    cdef _selection
    cdef _meta
    cdef CyBatch* ptr
    cdef meta_t m_meta
    cdef dict _internal
    cdef bool _owner
    cdef public bool Event
    cdef public bool Graph
    cdef public bool Selection

    def __init__(self): pass

    @staticmethod
    cdef Event make(CyBatch* bt):
        obj = <Event>Event.__new__(Event)
        obj.ptr = bt
        obj.ptr.Import(bt.meta)
        obj.Event = bt.this_ev != NULL
        obj.Graph = bt.this_gr != NULL
        obj.Selection = bt.this_sel != NULL
        obj._internal = {}
        return obj

    def __eq__(self, other):
        try: return self.hash == other.hash
        except: return False

    def __hash__(self):
        return int(self.hash[:8], 0)

    def __dealloc__(self):
        if not self._owner: return
        else: del self.ptr

    def __getattr__(self, str req):
        self.__getevent__()
        try:
            if self._event: pass
            else: raise AttributeError
            return getattr(self._event, req)
        except AttributeError: pass

        self.__getgraph__()
        try:
            if self._graph: pass
            else: raise AttributeError
            return getattr(self._graph, req)
        except AttributeError: pass

        self.__getselection__()
        try:
            if self._selection: pass
            else: raise AttributeError
            return getattr(self._selection, req)
        except AttributeError: pass

        try: return getattr(self.release_meta(), req)
        except AttributeError: pass

        try: return self._internal[req]
        except KeyError: raise AttributeError

    def __setattr__(self, str key, val):
        self.__getevent__()
        try: setattr(self._event, key, val)
        except AttributeError: pass

        self.__getgraph__()
        try: setattr(self._graph, key, val)
        except AttributeError: pass

        self.__getselection__()
        try: setattr(self._selection, key, val)
        except AttributeError: pass
        self._internal[key] = val

    def meta(self):
        if self._meta is not None: return self._meta
        else: return dereference(self.ptr.meta)

    cdef void __getevent__(self):
        if self._event is not None: return
        cdef CyEventTemplate* ev_ = self.ptr.this_ev
        if ev_ == NULL: self._event = False; return
        cdef CyCode* co_ = ev_.code_link
        if co_ == NULL: print("EVENT -> MISSING CODE!"); return

        c = Code()
        c.__setstate__(co_.ExportCode())
        cdef code_t co
        cdef pair[string, CyCode*] itr
        for itr in co_.dependency:
            co = itr.second.ExportCode()
            c.AddDependency([co])
        self._event = c.InstantiateObject

        cdef event_t ev = ev_.Export()
        cdef dict pkl = pickle.loads(ev.pickled_data)
        ev.pickled_data = b""
        self._event.__setstate__((pkl, ev))

    cdef void __getgraph__(self):
        if self._graph is not None: return
        cdef CyGraphTemplate* gr_ = self.ptr.this_gr
        if gr_ == NULL: self._graph = False; return
        cdef CyCode* co_ = gr_.code_link
        if co_ == NULL: print("GRAPH -> MISSING CODE!"); return

        c = Code()
        c.__setstate__(co_.ExportCode())
        gr = c.InstantiateObject
        if self._event is None: self._graph = gr()
        elif not self._event: self._graph = gr()
        else: self._graph = gr(self._event)
        self._graph.Import(gr_.Export())

    cdef void __getselection__(self):
        if self._selection is not None: return
        cdef CySelectionTemplate* sel_ = self.ptr.this_sel
        if sel_ == NULL: self._selection = False; return
        cdef CyCode* co_ = sel_.code_link
        if co_ == NULL: print("SELECTION -> MISSING CODE!"); return

        c = Code()
        c.__setstate__(co_.ExportCode())
        self._selection = c.InstantiateObject
        self._selection.__setstate__(sel_.Export())

    def release_selection(self):
        self.__getselection__()
        return self._selection

    def release_graph(self):
        self.__getgraph__()
        return self._graph

    def release_event(self):
        self.__getevent__()
        return self._event

    def release_meta(self):
        meta = MetaData()
        meta.__setstate__(self.meta())
        return meta

    def event_cache_dir(self):
        return map_to_dict(self.ptr.event_dir)

    def graph_cache_dir(self):
        return map_to_dict(self.ptr.graph_dir)

    def selection_cache_dir(self):
        return map_to_dict(self.ptr.selection_dir)

    def __getstate__(self) -> tuple:
        return (dereference(self.ptr.meta), self.ptr.ExportPickled())

    def __setstate__(self, tuple inpt):
        cdef batch_t b = inpt[1]
        self.m_meta = inpt[0]
        self.ptr = new CyBatch(b.hash)
        self.ptr.Import(&self.m_meta)
        self.ptr.ImportPickled(&b)
        self._owner = True

    @property
    def hash(self): return env(self.ptr.hash)

cdef class SampleTracer:

    cdef CySampleTracer* ptr
    cdef _Event
    cdef _Graph
    cdef dict _Selections
    cdef dict _graph_codes
    cdef int b_end
    cdef int b_start
    cdef int _nhashes
    cdef float memory_baseline
    cdef settings_t* _set
    cdef vector[CyBatch*] batches
    cdef export_t* _state

    def __cinit__(self):
        self.ptr = new CySampleTracer()
        self._set = &self.ptr.settings
        self._state = &self.ptr.state
        self._Event = None
        self._Graph = None
        self._Selections = {}
        self._graph_codes = {}
        self._nhashes = 0
        self.b_start = 0
        self.b_end = 0
        self.memory_baseline = -1

    def __dealloc__(self):
        del self.ptr

    def __init__(self):
        pass

    def __getstate__(self) -> tracer_t:
        return self.ptr.Export()

    def __setstate__(self, tracer_t inpt):
        self.ptr.Import(inpt)

    def __getitem__(self, key: Union[list, str]):
        self.preiteration()
        cdef vector[string] inpt;
        if isinstance(key, str): inpt = [enc(key)]
        else: inpt = penc(key)
        self._set.search = inpt
        cdef list output = self.makelist()
        self._set.search.clear()
        if not len(output): return False
        return output[0] if len(output) == 1 else output

    def __contains__(self, str val) -> bool:
        return self.__getitem__(val) != False

    def __len__(self) -> int:
        cdef map[string, int] f = self.ptr.length()
        cdef int entries = 0
        cdef string name = b""
        cdef string name_e = b""
        cdef string name_g = b""

        name_e = enc(self.Tree + "/" + self.EventName)
        if f.count(name_e): entries += f[name_e]
        else: name_e = b""

        name_g = enc(self.Tree + "/" + self.GraphName)
        if f.count(name_g): entries += f[name_g]
        else: name_g = b""

        if name_e.size(): name = name_e
        elif name_g.size(): name = name_g
        else: name = b""

        if not name.size():
            dc = {env(it.first) : it.second for it in f}
            self._nhashes = dc["n_hashes"]
            del dc["n_hashes"]
            return sum([entries for entries in dc.values()])
        return entries

    def __add__(self, SampleTracer other) -> SampleTracer:
        cdef SampleTracer out = self.clone()
        out.ptr.iadd(self.ptr)
        out.ptr.iadd(other.ptr)
        return out

    def __radd__(self, other) -> SampleTracer:
        if other == 0: return self
        return self.__add__(other)

    def __iadd__(self, SampleTracer other) -> SampleTracer:
        self.ptr.iadd(other.ptr)
        return self

    def __iter__(self):
        if self.preiteration(): return self
        self.batches = self.ptr.MakeIterable()
        self.b_end = self.batches.size()
        self.b_start = 0
        return self

    def __next__(self) -> Event:
        if self.b_end == self.b_start: raise StopIteration
        cdef Event event = Event.make(self.batches[self.b_start])
        self.b_start += 1
        return event


    # ------------------ CUSTOM FUNCTIONS ------------------ #
    def preiteration(self) -> bool:
        if not len(self.Tree):
            try: self.Tree = self.ShowTrees[0]
            except IndexError: return True

        if not len(self.EventName):
            try: self.EventName = self.ShowEvents[0]
            except IndexError: pass

        if not len(self.GraphName):
            try: self.GraphName = self.ShowGraphs[0]
            except IndexError: pass

        if not len(self.SelectionName):
            try: self.SelectionName = self.ShowSelections[0]
            except IndexError: pass

        if not len(self.EventName): pass
        else: self.GetEvent = True
        if not len(self.GraphName): pass
        else: self.GetGraph = True
        if not len(self.SelectionName): pass
        else: self.GetSelection = True
        return False

    def DumpTracer(self, retag = None):
        self.ptr.DumpTracer()
        cdef pair[string, meta_t] itr
        cdef meta_t meta

        cdef str entry, s_name
        cdef string root_n

        for itr in self._state.root_meta:
            root_n, meta = itr.first, itr.second
            entry = self.WorkingPath + "Tracer/"
            entry += env(root_n).rstrip(".root.1")
            try: os.makedirs("/".join(entry.split("/")[:-1]))
            except FileExistsError: pass
            entry += ".hdf5"

            f = h5py.File(entry, "a")
            ref = _check_h5(f, "meta")
            s_name = env(meta.sample_name)
            if retag is None: pass
            elif retag in s_name.split("|"): pass
            elif not len(s_name): meta.sample_name += enc(retag)
            else: meta.sample_name += enc("|" + retag)

            self.ptr.AddMeta(meta, root_n)
            ref.attrs.update({root_n : _encoder(meta)})
            tracer_dump(f, self._state, root_n)

            f.close()
        self.ptr.state = export_t()
        self._state = &self.ptr.state

    cdef void _deregister(self, ref, map[string, string] del_map):

        cdef map[string, string]* repl
        cdef pair[string, string] itr
        cdef str key

        for itr in del_map:
            key = env(itr.second)

            del ref[key + "_name_hash"]
            _check_h5(ref, key + "_name_hash")

            del ref[key + "_dir"]
            _check_h5(ref, key + "_dir")

            del ref["link_" + key + "_code"]
            _check_h5(ref, "link_" + key + "_code")

        cdef string path_, val_
        for key in ["event", "graph", "selection"]:
            if   key == "event":     repl = &self.ptr.link_event_code
            elif key == "graph":     repl = &self.ptr.link_graph_code
            elif key == "selection": repl = &self.ptr.link_selection_code

            for hash_, key in ref["link_" + key + "_code"].attrs.items():
                path_, val_ = enc(hash_), enc(key)
                if repl.count(path_): pass
                else: dereference(repl)[path_] = val_

    def RestoreTracer(self, dict tracers = {}, sample_name = None):
        cdef root_path = self.WorkingPath + "Tracer/"
        cdef str root, f
        cdef list files_ = []
        cdef list files

        if len(tracers): pass
        else: tracers = {root : files for root, _, files in os.walk(root_path)}
        for root, files in tracers.items():
            files_ += [root + "/" + f for f in files if f.endswith(".hdf5")]

        cdef meta_t meta
        cdef str key
        cdef string event_root
        cdef map[string, HDF5_t] data
        cdef map[string, string] del_map

        cdef str title = "TRACER::RESTORE ("
        _, bar = self._makebar(len(files_), title)
        for f in files_:
            f5 = h5py.File(f, "a")
            bar.set_description(title + f.split("/")[-1] + ")")
            bar.refresh()

            bar.update(1)
            data.clear()

            key = list(f5["meta"].attrs)[0]
            meta, event_root = _decoder(f5["meta"].attrs[key]), enc(key)
            if sample_name is None: pass
            elif sample_name in env(meta.sample_name).split("|"): pass
            else: f5.close(); continue

            self.ptr.AddMeta(meta, event_root)
            tracer_HDF5(f5, &data, b"event")
            tracer_HDF5(f5, &data, b"graph")
            tracer_HDF5(f5, &data, b"selection")
            del_map = self.ptr.RestoreTracer(&data, event_root)
            self._deregister(f5, del_map)
            if del_map.size(): f5.close(); continue

            for key, i in f5["code"].attrs.items():
                self._set.hashed_code[enc(key)] = _decoder(i)
                self.ptr.AddCode(self._set.hashed_code[enc(key)])
            f5.close()
        del bar

    cdef void _store_objects(self, map[string, vector[obj_t*]] cont, str _type):
        cdef str _short, _daod, out_path
        cdef str _path = self.WorkingPath + _type + "Cache/"

        cdef list spl
        cdef list prc = []
        cdef pair[string, vector[obj_t*]] itr
        for itr in cont:
            spl = env(itr.first).split(":")
            _daod, _short = spl[0], spl[1]
            out_path = _path + _short + "/" + _daod
            try: os.makedirs("/".join(out_path.split("/")[:-1]))
            except FileExistsError: pass

            out_path = out_path.rstrip(".root.1") + ".hdf5"
            prc.append([out_path, _short, recast_obj(itr.second, self._state, enc(out_path), itr.first)])
        if not len(prc): return
        th = Threading(prc, dump_objects, self.Threads, 1)
        th.Title = "TRACER::" + _type.upper() + "-SAVE: "
        th.Start()
        del th

    cdef _restore_objects(self, str type_, common_t getter, list these_hashes = [], bool quiet = False):
        cdef str title, file, key

        if type_ == "Event": self._set.getevent = True
        else: self._set.getevent = False

        if type_ == "Graph": self._set.getgraph = True
        else: self._set.getgraph = False

        if type_ == "Selection": self._set.getselection = True
        else: self._set.getselection = False

        self._set.get_all = True
        self._set.search = penc(these_hashes)
        self.MonitorMemory(type_)

        cdef list rest
        cdef CyBatch* bt
        cdef pair[string, vector[CyBatch*]] itc
        cdef map[string, vector[CyBatch*]] cache_map = self.ptr.RestoreCache(enc(type_))

        cdef int idy
        cdef int idx = 0
        cdef dict fetch_these = {}
        cdef vector[string] hashes

        for itc in cache_map:
            hashes.clear()
            for idy in prange(itc.second.size(), nogil = True, num_threads = 12):
                hashes.push_back(itc.second[idy].hash)
            fetch_these[itc.first] = [itc.first, type_, hashes]
            idx += itc.second.size()
        if not idx: return
        th = Threading(list(fetch_these.values()), fetch_objects, self.Threads, 1)
        th.Title = "RESTORING (" + type_.upper() + "): "
        th.Caller = self.Caller
        if quiet: th.Verbose = 0
        th.Start()
        for idx in range(len(th._lists)):
            rest = th._lists[idx]
            for bt in cache_map[rest[0]]:
                getter = rest[1][env(bt.hash)]
                bt.Import(&getter)
            th._lists[idx] = None
        del th
        self._set.search.clear()
        self._set.get_all = False
        self.ptr.length()

    def DumpEvents(self):
        self._store_objects(self.ptr.DumpEvents(), "Event")

    def DumpGraphs(self):
        self._store_objects(self.ptr.DumpGraphs(), "Graph")

    def DumpSelections(self):
        self._store_objects(self.ptr.DumpSelections(), "Selection")

    def RestoreEvents(self, list these_hashes = [], bool quiet = False):
        self._restore_objects("Event", event_t(), these_hashes, quiet)

    def RestoreGraphs(self, list these_hashes = [], bool quiet = False):
        self._restore_objects("Graph", graph_t(), these_hashes, quiet)

    def RestoreSelections(self, list these_hashes = [], bool quiet = False):
        self._restore_objects("Selection", selection_t(), these_hashes, quiet)

    cpdef vector[string] MonitorMemory(self, str type_):
        cdef CyBatch* batch
        if self.memory_baseline != -1: pass
        else: self.memory_baseline = psutil.virtual_memory()[3] / (1024**3)

        if psutil.virtual_memory()[3] / (1024**3) - self.memory_baseline < self.MaxRAM: return []
        cdef vector[string] lst = [batch.Hash() for batch in self.batches]
        if   type_ == "Event": self.ptr.FlushEvents(lst)
        elif type_ == "Graph": self.ptr.FlushGraphs(lst)
        elif type_ == "Selection": self.ptr.FlushSelections(lst)
        return lst

    def FlushEvents(self, list these_hashes = []):
        cdef str i
        if not len(these_hashes): return
        self.ptr.FlushEvents(<vector[string]>[enc(i) for i in these_hashes])

    def FlushGraphs(self, list these_hashes = []):
        cdef str i
        if not len(these_hashes): return
        self.ptr.FlushGraphs(<vector[string]>[enc(i) for i in these_hashes])

    def FlushSelections(self, list these_hashes = []):
        cdef str i
        if not len(these_hashes): return
        self.ptr.FlushSelections(<vector[string]>[enc(i) for i in these_hashes])

    def _makebar(self, inpt: Union[int], CustTitle: Union[None, str] = None):
        _dct = {}
        _dct["desc"] = f'Progress {self.Caller}' if CustTitle is None else CustTitle
        _dct["leave"] = True
        _dct["colour"] = "GREEN"
        _dct["dynamic_ncols"] = True
        _dct["total"] = inpt
        return (None, tqdm(**_dct))

    def trace_code(self, obj) -> code_t:
        if obj is None: raise AttributeError
        cdef code_t co = Code(obj).__getstate__()
        self.ptr.AddCode(co)
        return co

    def rebuild_code(self, val: Union[list, str, None]):
        cdef CyCode* c
        cdef string name
        cdef str name_s
        cdef output = []
        cdef pair[string, CyCode*] itc

        if isinstance(val, str):
            name = enc(val)
            if self.ptr.code_hashes.count(name): pass
            else: return output
            c = self.ptr.code_hashes[name]
            co = Code()
            co.__setstate__(c.ExportCode())
            output.append(co)
            return output

        elif isinstance(val, list):
            for name_s in val: output += self.rebuild_code(name_s)
            return output

        elif val is not None: return []
        for itc in self.ptr.code_hashes:
            output += self.rebuild_code(env(itc.first))
        return output

    def ImportSettings(self, settings_t inpt):
        self.ptr.ImportSettings(inpt)

    def ExportSettings(self) -> settings_t:
        return self.ptr.ExportSettings()

    def clone(self):
        return self.__class__()

    def is_self(self, inpt, obj = SampleTracer) -> bool:
        return issubclass(inpt.__class__, obj)

    cpdef dict makehashes(self):
        cdef int idx
        cdef dict out = {}
        cdef map[string, vector[string]] ev, gr, sel
        cdef vector[CyBatch*] br = self.ptr.MakeIterable()
        for idx in prange(br.size(), nogil = True, num_threads = br.size()):
            if self._set.getevent: merge(&ev, &br[idx].event_dir, br[idx].hash)
            if self._set.getgraph: merge(&gr, &br[idx].graph_dir, br[idx].hash)
            if self._set.getselection: merge(&sel, &br[idx].selection_dir, br[idx].hash)
        out["event"] = map_vector_to_dict(&ev)
        out["graph"] = map_vector_to_dict(&gr)
        out["selection"] = map_vector_to_dict(&sel)
        return out

    cpdef makelist(self, list hashes = [], bool as_export = False):
        cdef int i
        cdef CyBatch* bt
        cdef Event event
        cdef list output = []
        if len(hashes): self._set.search = penc(hashes)

        cdef map[string, event_t] exp_ev
        cdef map[string, graph_t] exp_gr
        cdef map[string, selection_t] exp_sel

        cdef vector[CyBatch*] batches = self.ptr.MakeIterable()
        if as_export:
            for i in prange(batches.size(), num_threads = 12, nogil = True):
                bt = batches[i]
                if bt.this_ev == NULL: pass
                else: exp_ev[bt.hash] = bt.this_ev.Export()

                if bt.this_gr == NULL: pass
                else: exp_gr[bt.hash] = bt.this_gr.Export()

                if bt.this_sel == NULL: pass
                else: exp_sel[bt.hash] = bt.this_sel.Export()
            return (exp_ev, exp_gr, exp_sel)

        for i in range(batches.size()):
            event = Event.make(batches[i])
            if self._set.getevent: pass
            else: event._event = False

            if self._set.getgraph: pass
            else: event._graph = False

            if self._set.getselection: pass
            else: event._selection = False
            output.append(event)
        return output

    def AddEvent(self, event_inpt, meta_inpt = None):
        cdef event_t event
        cdef code_t co
        cdef string name
        cdef dict pkl

        if meta_inpt is not None:
            pkl, event = event_inpt.__getstate__()
            event.pickled_data = pickle.dumps(pkl)
            name = event.event_name

            self.ptr.event_trees[event.event_tree] += 1
            if self.ptr.link_event_code.count(name): pass
            else: self.Event = event_inpt

            self.ptr.AddEvent(event, meta_inpt.__getstate__())
            return

        cdef str g
        cdef dict ef
        cdef list evnts = [ef for g in event_inpt for ef in event_inpt[g].values()]
        for ef in evnts: self.AddEvent(ef["Event"], ef["MetaData"])


    cpdef AddGraph(self, graph_inpt, meta_inpt = None):
        if graph_inpt is None: return
        if isinstance(graph_inpt, dict): self.ptr.AddGraph(graph_inpt, meta_t())
        elif meta_inpt is None: self.ptr.AddGraph(graph_inpt.__getstate__(), meta_t())
        else: self.ptr.AddGraph(graph_inpt.__getstate__(), meta_inpt.__getstate__())

    cpdef AddSelections(self, selection_inpt, meta_inpt = None):
        if selection_inpt is None: return
        if isinstance(selection_inpt, dict): self.ptr.AddSelection(selection_inpt, meta_t())
        elif meta_inpt is None: self.ptr.AddSelection(selection_inpt.__getstate__(), meta_t())
        else: self.ptr.AddSelection(selection_inpt.__getstate__(), meta_inpt.__getstate__())

    cpdef bool SetAttribute(self, fx, str name):
        if name in self._graph_codes: return False
        self._graph_codes[name] = fx
        if self._Graph is None: return True
        self.Graph = self._Graph
        self._graph_codes = {}
        return True

    @property
    def Event(self):
        if self.ptr.link_event_code.size(): pass
        elif self._Event is None: return
        else: return self._Event
        cdef pair[string, string] its
        for its in self.ptr.link_event_code:
            if self._set.eventname != its.first: continue
            co = self.rebuild_code(env(its.second))
            if not len(co): return None
            return co[0].InstantiateObject
        return None

    @Event.setter
    def Event(self, event):
        if event is None: return
        try: event = event()
        except: pass
        cdef code_t co
        cdef string name = enc(event.__name__())
        if type(event).__module__.endswith("cmodules.code"):
            co = event.code

            if self.ptr.code_hashes.count(co.hash): return
            self.ptr.link_event_code[name] = co.hash
            self.ptr.code_hashes[co.hash] = new CyCode()
            self.ptr.code_hashes[co.hash].ImportCode(co)
            return

        if not self.is_self(event, EventTemplate):
            return

        cdef map[string, code_t] deps = {}
        for o in event.Objects.values():
            co = self.trace_code(o)
            deps[co.hash] = co

        co = self.trace_code(event)
        self.ptr.link_event_code[name] = co.hash
        self.ptr.code_hashes[co.hash].AddDependency(deps)
        self._Event = event
        self._set.eventname = name
        self._set.getevent = True

    @property
    def Graph(self):
        cdef CyCode* code
        cdef dict features
        cdef pair[string, string] its
        cdef pair[string, string] its_

        for its in self.ptr.link_graph_code:
            if self._set.graphname != its.first: continue
            co = self.rebuild_code(env(its.second))
            if not len(co): return None
            code = self.ptr.code_hashes[its.second]
            features = {}
            for its_ in code.container.param_space:
                if its_.first == code.hash: continue
                if its_.first == b'__state__':
                    features["__state__"] = pickle.loads(its_.second)
                    continue
                c = self.rebuild_code(env(its_.first))
                if not len(c):continue
                features[env(its_.second)] = c[0]
            co = co[0].InstantiateObject
            setattr(co, "code", features)
            return co
        return None

    @Graph.setter
    def Graph(self, graph):
        if graph is None: return
        try: graph = graph()
        except TypeError: pass
        except Exception as err:
            self.Failure(str(err))
            self.Failure("Given Graph Implementation Failed to Initialize...")
            self.FailureExit("To debug this, try to initialize the object: <graph>()")
        cdef code_t co
        cdef graph_t gr
        cdef string name = enc(graph.__name__())
        cdef str name_
        if type(graph).__module__.endswith("cmodules.code"):
            co = graph.code
            if self.ptr.code_hashes.count(co.hash): return
            self.ptr.link_graph_code[name] = co.hash
            self.ptr.code_hashes[co.hash] = new CyCode()
            self.ptr.code_hashes[co.hash].ImportCode(co)
            return

        for name_, c_ in self._graph_codes.items():
            graph.__scrapecode__(c_, name_)
        co = self.trace_code(graph)
        self.ptr.link_graph_code[name] = co.hash
        cdef CyCode* c = self.ptr.code_hashes[co.hash]
        c.container.param_space[b'__state__'] = pickle.dumps(graph.__getstate__())
        for name_, o in graph.code.items():
            co = o.__getstate__()
            c.container.param_space[co.hash] = enc(name_)
            self.ptr.AddCode(co)
        self._Graph = graph
        self._set.graphname = name
        self._set.getgraph = True

    @property
    def Selections(self):
        if not len(self._Selections): return {}
        cdef CyCode* code
        cdef pair[string, string] its
        cdef string name
        cdef string params
        for its in self.ptr.link_selection_code:
            if env(its.first) not in self._Selections: continue
            co = self.rebuild_code(env(its.second))
            if not len(co): continue
            code = self.ptr.code_hashes[its.second]
            name = code.container.class_name
            co = co[0].InstantiateObject
            self._Selections[env(code.container.class_name)] = co
        return self._Selections

    @Selections.setter
    def Selections(self, selection):
        try: selection = selection()
        except: pass
        if not isinstance(selection, dict): pass
        else: self._Selections = selection

        if not self.is_self(selection, SelectionTemplate): return
        cdef code_t co = self.trace_code(selection)
        self.ptr.link_selection_code[co.class_name] = co.hash
        self._Selections[env(co.class_name)] = selection
        self._set.getselection = True

    @property
    def Model(self):
        c = Code()
        try:
            if not self._set.model.source_code.size(): return
            c.__setstate__(self._set.model)
            return c.InstantiateObject
        except Exception as err:
            self.Failure(str(err))
            self.Failure("Given Model Implementation Failed to Initialize...")
            self.FailureExit("To debug this, try to initialize the object: <model>()")

    @Model.setter
    def Model(self, val):
        if val is None: return
        self._set.model = Code(val).__getstate__()

    @property
    def ShowEvents(self) -> list:
        return map_to_list(self.ptr.link_event_code)

    @property
    def ShowGraphs(self) -> list:
        return map_to_list(self.ptr.link_graph_code)

    @property
    def ShowSelections(self) -> list:
        return map_to_list(self.ptr.link_selection_code)

    @property
    def ShowLength(self) -> dict:
        cdef pair[string, int] it
        cdef dict output = {}
        for it in self.ptr.length():
            if env(it.first) == "n_hashes": self._nhashes = it.second
            else: output[env(it.first)] = it.second
        return output

    @property
    def ShowTrees(self) -> list:
        return map_to_list(self.ptr.event_trees)

    @property
    def Files(self) -> dict:
        cdef dict output = {}
        cdef string k
        cdef pair[string, vector[string]] it
        for it in self._set.files: output[env(it.first)] = [env(k) for k in  it.second]
        return output

    @Files.setter
    def Files(self, val: Union[str, list, dict, None]):
        cdef dict Files = {}
        cdef str key, k
        if val is None: self._set.files.clear()
        elif isinstance(val, str): Files[""] = [val]
        elif isinstance(val, list): Files[""] = val
        elif isinstance(val, dict): Files.update(val)
        for key in Files:
            for k in Files[key]: self._set.files[enc(key)].push_back(enc(k))

    @property
    def WorkingPath(self):
        self.OutputDirectory = self.OutputDirectory
        cdef str path = ""
        path += self.OutputDirectory
        path += self.ProjectName
        return os.path.abspath(path) + "/"

    @property
    def SampleMap(self):
        cdef dict output = {}
        cdef string i
        cdef pair[string, vector[string]] itr
        for itr in self._set.samplemap:
            output[env(itr.first)] = pdec(&itr.second)
        return output

    @SampleMap.setter
    def SampleMap(self, val: Union[str, list, dict]):
        cdef dict state = self.SampleMap
        cdef str i, f
        if isinstance(val, str): state[val] = []
        elif isinstance(val, list):
            if "" in state: state[""] += val
            else: state[""] = val

        elif isinstance(val, dict):
            for i in val:
                if i not in state: state[i] = []
                state[i] += [k for k in val[i]]

        for i in state: self._set.samplemap[enc(i)] = penc(list(set(state[i])))

    @property
    def MaxRAM(self):
        if self._set.max_ram_memory == -1: pass
        else: return self._set.max_ram_memory
        self._set.max_ram_memory = psutil.virtual_memory()[0]/(1024**3)
        return self.MaxRAM

    @MaxRAM.setter
    def MaxRAM(self, float val):
        self._set.max_ram_memory = val

    @property
    def MaxGPU(self):
        if self._set.max_gpu_memory == -1: pass
        else: return self._set.max_gpu_memory
        if "cuda" not in self.Device: return -1
        try: self._set.max_gpu_memory = torch.cuda.mem_get_info(self.Device)[0]/(1024**3)
        except RuntimeError: self._set.max_gpu_memory = -1
        return self.MaxGPU

    @MaxGPU.setter
    def MaxGPU(self, float val):
        self._set.max_gpu_memory = val

    @property
    def Threads(self) -> int:
        return self._set.threads

    @Threads.setter
    def Threads(self, int val):
        self._set.threads = val

    @property
    def GetAll(self):
        return self._set.get_all

    @GetAll.setter
    def GetAll(self, bool val):
        self._set.get_all = val

    @property
    def EventCache(self):
        return self._set.eventcache

    @EventCache.setter
    def EventCache(self, bool val):
        self._set.eventcache = val

    @property
    def GetEvent(self):
        return self._set.getevent

    @GetEvent.setter
    def GetEvent(self, bool val):
        self._set.getevent = val

    @property
    def DataCache(self):
        return self._set.graphcache

    @DataCache.setter
    def DataCache(self, bool val):
        self._set.graphcache = val

    @property
    def GetGraph(self):
        return self._set.getgraph

    @GetGraph.setter
    def GetGraph(self, bool val):
        self._set.getgraph = val

    @property
    def GetSelection(self) -> bool:
        return self._set.getselection

    @GetSelection.setter
    def GetSelection(self, bool val):
        self._set.getselection = val

    @property
    def ProjectName(self) -> str:
        return env(self._set.projectname)

    @ProjectName.setter
    def ProjectName(self, str val):
        self._set.projectname = enc(val)

    @property
    def EventName(self) -> str:
        return env(self._set.eventname)

    @EventName.setter
    def EventName(self, val: Union[str, None]):
        if val is None: self._set.getevent = False
        else:
            self._set.eventname = enc(val)
            self._set.getevent = True

    @property
    def GraphName(self) -> str:
        return env(self._set.graphname)

    @GraphName.setter
    def GraphName(self, val: Union[str, None]):
        if val is None: self._set.getgraph = False
        else:
            self._set.graphname = enc(val)
            self._set.getgraph = True

    @property
    def SelectionName(self) -> str:
        return env(self._set.selectionname)

    @SelectionName.setter
    def SelectionName(self, val: Union[str, None]):
        if val is None: self._getselection = False
        else:
            self._set.selectionname = enc(val)
            self._set.getselection = True

    @property
    def Tree(self) -> str:
        return env(self._set.tree)

    @Tree.setter
    def Tree(self, str val):
        self._set.tree = enc(val)

    @property
    def OutputDirectory(self) -> str:
        return env(self._set.outputdirectory)

    @OutputDirectory.setter
    def OutputDirectory(self, str val):
        if not val.endswith("/"): val += "/"
        val = os.path.abspath(val)
        self._set.outputdirectory = enc(val +"/")

    @property
    def Caller(self) -> str:
        return env(self.ptr.caller)

    @Caller.setter
    def Caller(self, str val):
        self.ptr.caller = enc(val.upper())

    @property
    def EventStart(self):
        return self._set.event_start

    @EventStart.setter
    def EventStart(self, x: Union[int, None]):
        if x is None: x = 0
        self._set.event_start = x

    @property
    def EventStop(self):
        if self._set.event_stop == 0: return None
        return self._set.event_stop

    @EventStop.setter
    def EventStop(self, x: Union[int, None]):
        if x is None: x = 0
        self._set.event_stop = x

    @property
    def Verbose(self):
        return self._set.verbose

    @Verbose.setter
    def Verbose(self, int val):
        self._set.verbose = val

    @property
    def Chunks(self):
        return self._set.chunks

    @Chunks.setter
    def Chunks(self, int val):
        self._set.chunks = val

    @property
    def EnablePyAMI(self):
        return self._set.enable_pyami

    @EnablePyAMI.setter
    def EnablePyAMI(self, bool val):
        self._set.enable_pyami = val

    @property
    def Device(self):
        return env(self._set.device)

    @Device.setter
    def Device(self, str val):
        if val == "cpu": self._set.device = enc(val); return
        if not torch.cuda.device_count(): self._set.device = b"cpu"; return
        if ":" in val: self._set.device = enc(val)
        else: self._set.device = enc(val + ":" + str(range(torch.cuda.device_count())[0]))
        try: torch.cuda.mem_get_info()
        except AssertionError: self._set.device = b"cpu"

    @property
    def nHashes(self) -> int:
        return self._nhashes

    @property
    def TrainingName(self) -> str:
        return env(self._set.training_name)

    @TrainingName.setter
    def TrainingName(self, str val):
        self._set.training_name = enc(val)

    @property
    def RunName(self) -> str:
        return env(self._set.run_name)

    @RunName.setter
    def RunName(self, str val):
        self._set.run_name = enc(val)

    @property
    def Optimizer(self) -> str:
        return env(self._set.optimizer_name)

    @Optimizer.setter
    def Optimizer(self, str val):
        self._set.optimizer_name = enc(val)

    @property
    def OptimizerParams(self) -> dict:
        cdef pair[string, string] itr
        cdef dict output = {}
        for itr in self._set.optimizer_params:
            output[env(itr.first)] = pickle.loads(itr.second)
        return output

    @OptimizerParams.setter
    def OptimizerParams(self, dict val):
        cdef str key
        cdef string pkl
        self._set.optimizer_params.clear()
        for key in val:
            pkl = pickle.dumps(val[key])
            self._set.optimizer_params[enc(key)] = pkl

    @property
    def Scheduler(self) -> str:
        return env(self._set.scheduler_name)

    @Scheduler.setter
    def Scheduler(self, str val):
        self._set.scheduler_name = enc(val)

    @property
    def SchedulerParams(self) -> dict:
        cdef pair[string, string] itr
        cdef dict output = {}
        for itr in self._set.scheduler_params:
            output[env(itr.first)] = pickle.loads(itr.second)
        return output

    @SchedulerParams.setter
    def SchedulerParams(self, dict val):
        cdef str key
        cdef string pkl
        self._set.scheduler_params.clear()
        for key in val:
            pkl = pickle.dumps(val[key])
            self._set.scheduler_params[enc(key)] = pkl

    @property
    def kFolds(self):
        if self._set.kfolds < 0: return False
        return self._set.kfolds

    @kFolds.setter
    def kFolds(self, val):
        if val == False: self._set.kfolds = val
        else: self._set.kfolds = val

    @property
    def kFold(self):
        if not self._set.kfold.size(): return None
        if self._set.kfold.size() != 1: pass
        else: return self._set.kfold[0]
        return self._set.kfold

    @kFold.setter
    def kFold(self, val: Union[int, list, None]):
        cdef vector[int] val_
        if val is None: val_ = []
        elif isinstance(val, int): val_ = [val]
        else: val_ = val
        self._set.kfold = val_

    @property
    def Epoch(self):
        if not self._set.epoch.size(): return None
        else: return self._set.epoch

    @Epoch.setter
    def Epoch(self, val: Union[int, list, dict]):
        cdef int k, i
        self._set.epoch.clear()
        if isinstance(val, int):
            for k in self._set.kfold: self._set.epoch[k] = val
        if isinstance(val, list):
            for i, k in zip(val, self.kFold): self._set.epoch[k] = i
        if isinstance(val, dict):
            for k, i in val.items(): self._set.epoch[k] = i

    @property
    def Epochs(self):
        if self._set.epochs == -1: return None
        return self._set.epochs

    @Epochs.setter
    def Epochs(self, int val):
        self._set.epochs = val

    @property
    def KinematicMap(self) -> dict:
        cdef dict output = {}
        cdef pair[string, string] itr
        for itr in self._set.kinematic_map:
            output[env(itr.first)] = env(itr.second)
        return output

    @KinematicMap.setter
    def KinematicMap(self, dict val):
        cdef str key
        cdef string pkl
        self._set.kinematic_map.clear()
        for key in val: self._set.kinematic_map[enc(key)] = enc(val[key])

    @property
    def ModelParams(self) -> dict:
        cdef pair[string, string] itr
        cdef dict output = {}
        for itr in self._set.model_params:
            output[env(itr.first)] = pickle.loads(itr.second)
        return output

    @ModelParams.setter
    def ModelParams(self, dict val):
        cdef str key
        cdef string pkl
        self._set.model_params.clear()
        for key in val:
            pkl = pickle.dumps(val[key])
            self._set.model_params[enc(key)] = pkl

    @property
    def DebugMode(self) -> bool:
        return self._set.debug_mode

    @DebugMode.setter
    def DebugMode(self, bool val):
        self._set.debug_mode = val

    @property
    def ContinueTraining(self) -> bool:
        return self._set.continue_training

    @ContinueTraining.setter
    def ContinueTraining(self, bool val):
        self._set.continue_training = val

    @property
    def SortByNodes(self) -> bool:
        return self._set.sort_by_nodes

    @SortByNodes.setter
    def SortByNodes(self, bool val):
        self._set.sort_by_nodes = val

    @property
    def EnableReconstruction(self) -> bool:
        return self._set.enable_reconstruction

    @EnableReconstruction.setter
    def EnableReconstruction(self, bool val):
        self._set.enable_reconstruction = val

    @property
    def BatchSize(self):
        return self._set.batch_size

    @BatchSize.setter
    def BatchSize(self, int val):
        self._set.batch_size = val

    @property
    def PlotLearningMetrics(self):
        return self._set.runplotting

    @PlotLearningMetrics.setter
    def PlotLearningMetrics(self, bool val):
        self._set.runplotting = val

    @property
    def TrainingSize(self):
        if self._set.training_size < 0: return False
        else: return self._set.training_size

    @TrainingSize.setter
    def TrainingSize(self, val):
        self._set.training_size = val

