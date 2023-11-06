# distutils: language = c++
# cython: language_level = 3

from AnalysisG._cmodules.ParticleTemplate import ParticleTemplate
from torch_geometric.data import Data
from AnalysisG.Tools import Code
import pickle
import torch

from cygraph cimport CyGraphTemplate
from cycode cimport CyCode

from cytypes cimport graph_t, event_t, meta_t
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map, pair
from libcpp cimport bool

cdef string enc(str val): return val.encode("UTF-8")
cdef str env(string val): return val.decode("UTF-8")

cdef class wEvent:
    cdef public event
    def __cinit__(self): pass
    def __init__(self): self.event = None
    def __getattr__(self, inpt):
        try: return getattr(self.event, inpt)
        except AttributeError: pass
        if self.event is None: return []
        return None
    def get(self): return self.event


cdef class wParticle:
    cdef particle
    def __init__(self, inpt): self.particle = inpt
    def __getattr__(self, inpt):
        try: return getattr(self.particle, inpt)
        except AttributeError: return None
    def get(self): return self.particle


cdef class GraphTemplate:

    cdef CyGraphTemplate* ptr
    cdef graph_t* gr
    cdef _event
    cdef list _particles
    cdef dict _code
    cdef bool _loaded
    cdef _data

    def __cinit__(self):
        self.ptr = new CyGraphTemplate()
        cdef str x = self.__class__.__name__
        self.gr = &(self.ptr.graph)
        self.ptr.set_event_name(self.gr, enc(x))
        self._data = None
        self._code = {}
        self._loaded = False
        self._event = wEvent()
        self._particles = []

    def __init__(self):
        if ".code" in type(self).__module__: return
        try: self.__scrapecode__(self, self.__class__.__name__)
        except AttributeError: pass

    def __dealloc__(self): del self.ptr
    def __name__(self) -> str: return env(self.gr.event_name)
    def __hash__(self) -> int: return int(self.hash[:8], 0)
    def __eq__(self, other) -> bool:
        if not self.is_self(other): return False
        cdef GraphTemplate o = other
        return self.ptr[0] == o.ptr[0]

    def __getattr__(self, inpt):
        try: return getattr(self.__data__(), inpt)
        except: return None

    def __getstate__(self) -> graph_t:
        return self.ptr.Export()

    def __setstate__(self, graph_t gr):
        self.ptr.Import(gr)

    def __data__(self):
        if self._loaded: return self._data
        if self.gr.skip_graph: return None
        cdef string pkl = self.gr.pickled_data
        self._data = pickle.loads(pkl)
        self._loaded = True
        return self._data

    def __scrapecode__(self, fx, str key):
        cdef str name = type(fx).__module__
        if self.is_self(fx): pass
        elif ".code" not in name: name = fx.__name__
        elif fx.is_class: name = fx.class_name
        elif fx.is_function: name = fx.function_name
        else: name = ""
        if len(key) == 4: key += name

        cdef string k = enc(key)
        if not self.ptr.code_owner: return self._code[key]
        elif not self.ptr.graph_fx.count(k): pass
        elif not self.ptr.node_fx.count(k): pass
        elif not self.ptr.edge_fx.count(k): pass
        elif not self.ptr.pre_sel_fx.count(k): pass
        elif not self.ptr.topo_link is not NULL: pass
        elif not self.ptr.code_link is not NULL: pass
        else: return self._code[key]

        co_ = Code(fx)
        self._code[key] = co_
        self._code[co_.hash] = co_
        cdef CyCode* co = new CyCode()
        co.ImportCode(co_.__getstate__())
        co.Hash()
        if key.startswith("G_"):
            self.ptr.graph_fx[k] = co
            self.gr.graph_feature[k] = co.hash

        elif key.startswith("N_"):
            self.ptr.node_fx[k] = co
            self.gr.node_feature[k] = co.hash

        elif key.startswith("E_"):
            self.ptr.edge_fx[k] = co
            self.gr.edge_feature[k] = co.hash

        elif key.startswith("P_"):
            self.ptr.pre_sel_fx[k] = co
            self.gr.pre_sel_feature[k] = co.hash

        elif key.startswith("T_"): self.ptr.topo_link = co
        else: self.ptr.code_link = co
        return co_

    def AddGraphFeature(self, fx, str name = ""):
        self.__scrapecode__(fx, "G_F_" + name)

    def AddNodeFeature(self, fx, str name = ""):
        self.__scrapecode__(fx, "N_F_" + name)

    def AddEdgeFeature(self, fx, str name = ""):
        self.__scrapecode__(fx, "E_F_" + name)

    def AddGraphTruthFeature(self, fx, str name = ""):
        self.__scrapecode__(fx, "G_T_" + name)

    def AddNodeTruthFeature(self, fx, str name = ""):
        self.__scrapecode__(fx, "N_T_" + name)

    def AddEdgeTruthFeature(self, fx, str name = ""):
        self.__scrapecode__(fx, "E_T_" + name)

    def AddPreSelection(self, fx, str name = ""):
        self.__scrapecode__(fx, "P_F_" + name)

    def SetTopology(self, fx = None):
        cdef map[string, int] particles
        cdef vector[int] src_dst
        cdef string p_hash
        cdef int src, dst
        if isinstance(fx, list):
            self.gr.src_dst.clear()
            particles = self.gr.hash_particle
            for src_dst in fx:
                src, dst = src_dst
                p_hash = self.ptr.IndexToHash(src)
                self.gr.src_dst[p_hash].push_back(dst)
            return
        if fx is None: return self.ptr.FullyConnected()
        fx = self.__scrapecode__(fx, "T_F_")
        cdef list tmp = self.Topology
        self.gr.src_dst.clear()
        for src_dst in tmp:
            src = src_dst[0]
            dst = src_dst[1]
            p1 = self._particles[src]
            p2 = self._particles[dst]
            if not fx(p1, p2): continue
            p_hash = self.ptr.IndexToHash(src)
            self.gr.src_dst[p_hash].push_back(dst)

    def __buildthis__(self, str key, str co_hash, bool preselection, list this):
        try:
            res = self._code[co_hash](*this)
            if res is None: raise TypeError("AttributeError")
        except Exception as inst:
            if key.startswith("G_F_"): key = "G_" + key[4:]
            if key.startswith("N_F_"): key = "N_" + key[4:]
            if key.startswith("E_F_"): key = "E_" + key[4:]
            self.gr.errors[enc(key)] = enc(str(inst))
            return False

        if preselection and res: return True
        if not preselection:
            key = type(res).__name__
            if key == "bool": return [torch.tensor(res, dtype = torch.bool).view(1, -1)]
            if key == "float": return [torch.tensor(res, dtype = torch.float64).view(1, -1)]
            if key == "int": return [torch.tensor(res, dtype = torch.int).view(1, -1)]
            return [torch.tensor(res).view(1, -1)]
        self.gr.presel[enc(key)]+=1
        self.gr.skip_graph = True
        return False

    def Build(self):
        cdef pair[string, string] itr
        cdef list topo, content, src_dst
        cdef int n_num, src, dst
        cdef str key

        self.SetTopology()
        for key in self._code:
            if not key.startswith("T_F_"): continue
            self.SetTopology(self._code[key])
            break
        topo = self.Topology
        if self.gr.empty_graph: return

        for itr in self.gr.pre_sel_feature:
            key = env(itr.first)
            co_h = env(itr.second)
            if self.__buildthis__(key, co_h, True, [self._event.get()]): continue
            return

        n_num = self.gr.hash_particle.size()
        data = Data(edge_index = torch.tensor(topo, dtype = torch.long).t())
        data.num_nodes = torch.tensor(n_num, dtype = torch.int)
        setattr(data, "i", torch.tensor([self.index], dtype = torch.int))
        for itr in self.gr.graph_feature:
            key = env(itr.first)
            co_h = env(itr.second)
            res = self.__buildthis__(key, co_h, False, [self._event.get()])
            if not res: continue
            if key.startswith("G_F_"): key = "G_" + key[4:]
            setattr(data, key, res[0])

        for itr in self.gr.node_feature:
            key = env(itr.first)
            co_h = env(itr.second)
            content = []
            for src in range(n_num):
                src = self.gr.hash_particle[self.ptr.IndexToHash(src)]
                res = self.__buildthis__(key, co_h, False, [self._particles[src].get()])
                if not res: content = []; break
                content += res
            if not len(content): continue
            if key.startswith("N_F_"): key = "N_" + key[4:]
            setattr(data, key, torch.cat(content, dim = 0))

        for itr in self.gr.edge_feature:
            key = env(itr.first)
            co_h = env(itr.second)
            content = []
            for src_dst in topo:
                src, dst = src_dst[0], src_dst[1]
                src = self.gr.hash_particle[self.ptr.IndexToHash(src)]
                dst = self.gr.hash_particle[self.ptr.IndexToHash(dst)]
                src_dst = [self._particles[src].get(), self._particles[dst].get()]
                res = self.__buildthis__(key, co_h, False, src_dst)
                if not res: content = []; break
                content+=res
            if not len(content): continue
            if key.startswith("E_F_"): key = "E_" + key[4:]
            setattr(data, key, torch.cat(content, dim = 0))

        self._particles = []
        self._event = None
        self._code = {}
        try: data.validate(); self.gr.pickled_data = pickle.dumps(data)
        except: self.gr.errors[b'PyG::GraphError'] = b"Invalid data"

    @property
    def Topology(self) -> list:
        cdef list output = []
        cdef int src, dst
        cdef pair[string, vector[int]] it
        for it in self.gr.src_dst:
            src = self.gr.hash_particle[it.first]
            for dst in it.second: output.append([src, dst])
        if not len(output): self.gr.empty_graph = True;
        else: self.gr.empty_graph = False
        return output

    @property
    def Export(self) -> graph_t:
        return self.ptr.Export()

    def ImportCode(self, dict inpt):
        cdef str key
        for i in inpt:
            if i.startswith("__"): continue
            self._code[inpt[i].hash] = inpt[i]
        self.code_owner = False

    @property
    def Event(self):
        return self._event

    @Event.setter
    def Event(self, event):
        if event is None: return
        self._event.event = event

        cdef event_t ev
        ev.event_hash    = enc(event.hash)
        ev.event_tagging = enc(event.Tag)
        ev.event_tree    = enc(event.Tree)
        ev.event_root    = enc(event.ROOT)
        ev.event_index   = event.index
        ev.weight        = event.weight
        self.ptr.RegisterEvent(&ev)

    @property
    def Particles(self):
        return [i for i in self._particles]

    @Particles.setter
    def Particles(self, val):
        cdef int k
        cdef string hash
        if not isinstance(val, list): val = [val]
        for k in range(len(val)):
            hash = enc(val[k].hash)
            self.ptr.AddParticle(hash, k)
            self._particles.append(wParticle(val[k]))

    def ParticleToIndex(self, val) -> int:
        if not issubclass(val.__class__, ParticleTemplate): return -1
        cdef string hash_ = enc(val.hash)
        if not self.gr.hash_particle.count(hash_): return -1
        return self.gr.hash_particle[hash_]

    def is_self(self, inpt) -> bool:
        if isinstance(inpt, GraphTemplate): return True
        return issubclass(inpt.__class__, GraphTemplate)

    def ImportMetaData(self, meta_t meta):
        self.ptr.ImportMetaData(meta)

    def Import(self, graph_t graph):
        self.ptr.Import(graph)

    def clone(self):
        x = self.__class__
        x._code = self._code
        return x

    @property
    def self_loops(self) -> bool:
        return self.gr.self_loops

    @self_loops.setter
    def self_loops(self, bool val):
        self.gr.self_loops = val

    @property
    def code_owner(self) -> bool:
        return self.ptr.code_owner

    @code_owner.setter
    def code_owner(self, bool val):
        self.ptr.code_owner = val

    @property
    def code(self) -> dict:
        return self._code

    @property
    def index(self) -> int:
        return self.gr.event_index

    @property
    def Errors(self) -> dict:
        cdef pair[string, string] it
        return {env(it.first) : env(it.second) for it in self.gr.errors}

    @property
    def PreSelectionMetric(self) -> dict:
        cdef pair[string, int] it
        return {env(it.first) : it.second for it in self.gr.presel}

    @property
    def Train(self) -> bool:
        return self.gr.train

    @Train.setter
    def Train(self, bool val):
        self.gr.train = val

    @property
    def Eval(self) -> bool:
        return self.gr.evaluation

    @Eval.setter
    def Eval(self, bool val):
        self.gr.evaluation = val

    @property
    def Validation(self) -> bool:
        return self.gr.validation

    @Validation.setter
    def Validation(self, bool val):
        self.gr.validation = val

    @property
    def EmptyGraph(self) -> bool:
        return self.gr.empty_graph

    @EmptyGraph.setter
    def EmptyGraph(self, bool val):
        self.gr.empty_graph = val

    @property
    def SkipGraph(self) -> bool:
        return self.gr.skip_graph

    @SkipGraph.setter
    def SkipGraph(self, bool val):
        self.gr.skip_graph = val

    @property
    def Tag(self) -> str:
        return env(self.gr.event_tagging)

    @Tag.setter
    def Tag(self, str val):
        self.gr.event_tagging = enc(val)

    @property
    def cached(self) -> bool:
        return self.gr.cached

    @cached.setter
    def cached(self, bool val) -> bool:
        self.gr.cached = val

    @property
    def Tree(self) -> str:
        return env(self.gr.event_tree)

    @property
    def ROOT(self) -> str:
        return env(self.gr.event_root)

    @property
    def hash(self) -> str:
        return env(self.ptr.Hash())

    @property
    def Graph(self) -> bool:
        return self.ptr.is_graph

    @property
    def GraphName(self) -> bool:
        return env(self.gr.event_name)
